from markupsafe import Markup, escape

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreateProjectLineWizard(models.TransientModel):
    _name = 'create.project.line.wizard'
    _description = 'Create Project for Sale Order Line'

    sale_line_id = fields.Many2one('sale.order.line', required=True, readonly=True)
    project_template_id = fields.Many2one(
        'project.project',
        string='Project Template',
        domain="[('is_template', '=', True)]",
        required=True,
    )
    payment_warning = fields.Char(compute='_compute_payment_warning')
    task_tree_html = fields.Html(
        string='Task Preview',
        compute='_compute_task_tree_html',
        sanitize=False,
    )

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
                wiz.task_tree_html = False
                continue

            tasks = template.sudo().task_ids.sorted(lambda t: (t.sequence, t.id))
            if not tasks:
                wiz.task_tree_html = Markup(
                    '<p class="text-muted fst-italic">No tasks in this template.</p>'
                )
                continue

            # Build parent→children map
            children_map = {}
            roots = []
            for task in tasks:
                children_map.setdefault(task.parent_id.id, []).append(task)
                if not task.parent_id:
                    roots.append(task)

            wiz.task_tree_html = _render_tree(roots, children_map)

    def action_create_project(self):
        """Create project + task from template for the SO line."""
        self.ensure_one()
        sol = self.sale_line_id

        if sol.project_id:
            raise UserError(_("A project already exists for this line."))

        # Temporarily set the template on the product if user changed it
        original_template = sol.product_id.project_template_id
        if self.project_template_id != original_template:
            sol.product_id.project_template_id = self.project_template_id

        try:
            project = sol.sudo()._timesheet_create_project()
            sol.sudo()._timesheet_create_task(project)
        finally:
            # Restore original template
            if self.project_template_id != original_template:
                sol.product_id.project_template_id = original_template

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }


TREE_CSS = """
<style>
.task-tree { font-family: monospace; font-size: 13px; line-height: 1.8; padding: 8px 0; }
.task-tree .node { display: flex; align-items: baseline; }
.task-tree .connector { color: #999; white-space: pre; margin-right: 6px; }
.task-tree .name { color: #333; }
.task-tree .children { padding-left: 24px; }
</style>
"""


def _render_tree(roots, children_map):
    """Render a list of root tasks as an HTML tree."""
    html = Markup(TREE_CSS) + Markup('<div class="task-tree">')
    for i, task in enumerate(roots):
        is_last = (i == len(roots) - 1)
        html += _render_node(task, children_map, is_last)
    html += Markup('</div>')
    return html


def _render_node(task, children_map, is_last):
    """Render a single task node with its children."""
    connector = '└─ ' if is_last else '├─ '
    html = Markup('<div class="node">')
    html += Markup('<span class="connector">%s</span>') % connector
    html += Markup('<span class="name">%s</span>') % escape(task.name)
    html += Markup('</div>')

    children = children_map.get(task.id, [])
    if children:
        html += Markup('<div class="children">')
        for j, child in enumerate(children):
            child_is_last = (j == len(children) - 1)
            html += _render_node(child, children_map, child_is_last)
        html += Markup('</div>')

    return html
