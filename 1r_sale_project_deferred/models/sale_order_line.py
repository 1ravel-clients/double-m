from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    amount_paid = fields.Monetary(
        string='Paid',
        compute='_compute_amount_paid',
        currency_field='currency_id',
    )

    def _compute_amount_paid(self):
        for sol in self:
            invoices = sol.invoice_lines.mapped('move_id').filtered(
                lambda m: m.state == 'posted' and m.move_type == 'out_invoice'
            )
            sol.amount_paid = sum(
                inv.amount_total - inv.amount_residual for inv in invoices
            )

    def action_open_project(self):
        """Navigate to the linked project."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_project_wizard(self):
        """Open the per-line project creation wizard."""
        self.ensure_one()
        wizard = self.env['create.project.line.wizard'].create({
            'sale_line_id': self.id,
            'project_template_id': self.product_id.project_template_id.id,
        })
        return {
            'name': 'Create Project',
            'type': 'ir.actions.act_window',
            'res_model': 'create.project.line.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }
