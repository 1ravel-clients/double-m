from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CreateProjectWizard(models.TransientModel):
    _name = 'create.project.wizard'
    _description = 'Create Projects from Sale Order'

    sale_order_id = fields.Many2one('sale.order', required=True, readonly=True)
    show_all = fields.Boolean(
        string='Show All Lines',
        help='Include unpaid and uninvoiced lines',
    )
    line_ids = fields.One2many(
        'create.project.wizard.line', 'wizard_id',
        compute='_compute_line_ids', store=True, readonly=False,
    )

    @api.depends('sale_order_id', 'show_all')
    def _compute_line_ids(self):
        for wizard in self:
            wizard.line_ids = [(5, 0, 0)]
            if not wizard.sale_order_id:
                continue

            eligible = wizard.sale_order_id.order_line.filtered(
                lambda l: l.product_id.project_template_id
                and l.product_id.service_tracking == 'no'
                and not l.project_id
            )

            vals_list = []
            for sol in eligible:
                invoices = sol.invoice_lines.mapped('move_id').filtered(
                    lambda m: m.state == 'posted' and m.move_type == 'out_invoice'
                )
                if invoices:
                    states = invoices.mapped('payment_state')
                    if 'paid' in states or 'in_payment' in states:
                        status = 'paid'
                    elif 'partial' in states:
                        status = 'partial'
                    else:
                        status = 'not_paid'
                    amount = sum(invoices.mapped('amount_total'))
                else:
                    status = 'not_invoiced'
                    amount = 0.0

                is_paid = status in ('paid', 'partial')
                if not wizard.show_all and not is_paid:
                    continue

                vals_list.append((0, 0, {
                    'sale_line_id': sol.id,
                    'selected': is_paid,
                    'payment_status': status,
                    'invoiced_amount': amount,
                }))

            wizard.line_ids = vals_list

    def action_create_projects(self):
        """Create one project + task per selected line."""
        self.ensure_one()
        selected = self.line_ids.filtered('selected')
        if not selected:
            raise UserError(_('Please select at least one line.'))

        created_projects = self.env['project.project']
        for wiz_line in selected:
            sol = wiz_line.sale_line_id.sudo()
            project = sol._timesheet_create_project()
            sol._timesheet_create_task(project)
            created_projects |= project

        if len(created_projects) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'res_id': created_projects.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'name': _('Created Projects'),
            'domain': [('id', 'in', created_projects.ids)],
            'view_mode': 'list,form',
            'target': 'current',
        }


class CreateProjectWizardLine(models.TransientModel):
    _name = 'create.project.wizard.line'
    _description = 'Create Project Wizard Line'

    wizard_id = fields.Many2one('create.project.wizard', required=True, ondelete='cascade')
    sale_line_id = fields.Many2one('sale.order.line', required=True, readonly=True)
    selected = fields.Boolean(string='Create?')
    product_name = fields.Char(related='sale_line_id.product_id.name', readonly=True)
    quantity = fields.Float(related='sale_line_id.product_uom_qty', readonly=True)
    payment_status = fields.Selection([
        ('not_invoiced', 'Not Invoiced'),
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ], readonly=True)
    invoiced_amount = fields.Monetary(readonly=True, currency_field='currency_id')
    currency_id = fields.Many2one(related='sale_line_id.currency_id', readonly=True)
