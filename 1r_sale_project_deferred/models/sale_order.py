from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    deferred_project_eligible = fields.Boolean(
        compute='_compute_deferred_project_eligible',
    )

    def _compute_deferred_project_eligible(self):
        """True if SO has lines eligible for deferred project creation."""
        for order in self:
            order.deferred_project_eligible = bool(
                order.order_line.filtered(
                    lambda l: l.product_id.project_template_id
                    and l.product_id.service_tracking == 'no'
                    and not l.project_id
                )
            )

    def action_create_project_wizard(self):
        """Open the deferred project creation wizard."""
        self.ensure_one()
        wizard = self.env['create.project.wizard'].create({
            'sale_order_id': self.id,
        })
        return {
            'name': 'Create Projects',
            'type': 'ir.actions.act_window',
            'res_model': 'create.project.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }
