from markupsafe import Markup, escape

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreateProjectLineWizard(models.TransientModel):
    _name = 'create.project.line.wizard'
    _description = 'Create Project for Sale Order Line'

    sale_line_id = fields.Many2one('sale.order.line', required=True, readonly=True)
    project_name = fields.Char(
        string='Project Name',
        compute='_compute_project_name',
        store=True,
        readonly=False,
    )
    project_template_id = fields.Many2one(
        'project.project',
        string='Project Template',
        domain="[('is_template', '=', True)]",
    )
    payment_warning = fields.Char(compute='_compute_payment_warning')
    task_tree_html = fields.Html(
        string='Tasks Preview',
        compute='_compute_task_tree_html',
        sanitize=False,
    )

    @api.depends('sale_line_id')
    def _compute_project_name(self):
        for wiz in self:
            sol = wiz.sale_line_id
            so_name = sol.order_id.name or ''
            product_name = sol.product_id.name or ''
            wiz.project_name = '%s - %s' % (so_name, product_name)

    @api.depends('sale_line_id')
    def _compute_payment_warning(self):
        for wiz in self:
            sol = wiz.sale_line_id
            invoices = sol.invoice_lines.mapped('move_id').filtered(
                lambda m: m.state == 'posted' and m.move_type == 'out_invoice'
            )
            if not invoices:
                wiz.payment_warning = _("This line has not been invoiced yet.")
            elif all(inv.payment_state == 'not_paid' for inv in invoices):
                wiz.payment_warning = _("Invoice has not been paid.")
            elif any(inv.payment_state == 'partial' for inv in invoices):
                wiz.payment_warning = _("Invoice is only partially paid.")
            else:
                wiz.payment_warning = False

    @api.depends('project_template_id')
    def _compute_task_tree_html(self):
        for wiz in self:
            template = wiz.project_template_id
            if not template:
                wiz.task_tree_html = Markup(
                    '<div style="padding:16px 0;color:#888;font-style:italic;">'
                    'No template selected — an empty project will be created.'
                    '</div>'
                )
                continue

            tasks = template.sudo().task_ids.sorted(lambda t: (t.sequence, t.id))
            if not tasks:
                wiz.task_tree_html = Markup(
                    '<div style="padding:16px 0;color:#888;font-style:italic;">'
                    'This template has no tasks.'
                    '</div>'
                )
                continue

            # Build parent→children map
            children_map = {}
            roots = []
            for task in tasks:
                children_map.setdefault(task.parent_id.id, []).append(task)
                if not task.parent_id:
                    roots.append(task)

            wiz.task_tree_html = _render_task_cards(roots, children_map)

    def action_create_project(self):
        """Create project from template without mutating the product record."""
        self.ensure_one()
        sol = self.sale_line_id.sudo()

        if sol.project_id:
            raise UserError(_("A project already exists for this line."))

        # Build project values using the native helper
        values = sol._timesheet_create_project_prepare_values()
        values['name'] = self.project_name or values['name']

        template = self.project_template_id
        if template:
            # Copy from template (same as native _timesheet_create_project)
            if template.is_template:
                project = template.action_create_from_template(values)
            else:
                project = template.copy(values)
            project.tasks.write({
                'sale_line_id': sol.id,
                'partner_id': sol.order_id.partner_id.id,
            })
            project.tasks.filtered('parent_id').write({
                'sale_line_id': sol.id,
                'sale_order_id': sol.order_id.id,
            })
        else:
            # Create empty project
            project = self.env['project.project'].sudo().create(values)

        # Create default stages if none
        if not project.type_ids:
            project.type_ids = self.env['project.task.type'].sudo().create([
                {'name': _('To Do'), 'fold': False, 'sequence': 5},
                {'name': _('In Progress'), 'fold': False, 'sequence': 10},
                {'name': _('Done'), 'fold': False, 'sequence': 15},
                {'name': _('Cancelled'), 'fold': True, 'sequence': 20},
            ])

        # Link project to SO line (same as native)
        sol.write({'project_id': project.id})
        project.reinvoiced_sale_order_id = sol.order_id

        # Create task in the project
        sol._timesheet_create_task(project)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }


# ---------------------------------------------------------------------------
# Trello-style task card rendering
# ---------------------------------------------------------------------------

CARD_STYLE = (
    'display:inline-block;vertical-align:top;background:#fff;border:1px solid #dee2e6;'
    'border-radius:8px;padding:10px 14px;margin:4px;min-width:160px;max-width:220px;'
    'box-shadow:0 1px 2px rgba(0,0,0,.06);'
)
CHILD_STYLE = (
    'font-size:12px;color:#666;margin-top:6px;padding-top:6px;'
    'border-top:1px solid #eee;'
)
CHILD_ITEM_STYLE = 'padding:1px 0;'
CONTAINER_STYLE = 'display:flex;flex-wrap:wrap;gap:6px;padding:8px 0;'


def _render_task_cards(roots, children_map):
    """Render root tasks as Trello-style cards with subtasks listed inside."""
    html = Markup('<div style="%s">') % CONTAINER_STYLE
    for task in roots:
        html += _render_card(task, children_map)
    html += Markup('</div>')
    return html


def _render_card(task, children_map):
    """Render a single task card."""
    html = Markup('<div style="%s">') % CARD_STYLE
    html += Markup('<div style="font-weight:600;font-size:13px;">%s</div>') % escape(task.name)

    children = children_map.get(task.id, [])
    if children:
        html += Markup('<div style="%s">') % CHILD_STYLE
        for child in children:
            html += Markup('<div style="%s">') % CHILD_ITEM_STYLE
            html += Markup('&#8226; %s') % escape(child.name)
            html += Markup('</div>')
            # Show grandchildren inline too
            grandchildren = children_map.get(child.id, [])
            for gc in grandchildren:
                html += Markup(
                    '<div style="%s padding-left:12px;color:#999;">'
                ) % CHILD_ITEM_STYLE
                html += Markup('&#8226; %s') % escape(gc.name)
                html += Markup('</div>')
        html += Markup('</div>')

    html += Markup('</div>')
    return html
