from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_apply_expense_pool_distribution(self):
        """Fill analytic distribution on invoice lines using expense-pool weights."""
        self.ensure_one()
        if self.move_type != 'in_invoice':
            raise UserError(_("This action is only available for vendor bills."))

        target_date = self.invoice_date or fields.Date.context_today(self)
        distribution = self.env['expense.pool.snapshot'].get_distribution_for_date(target_date)

        if not distribution:
            raise UserError(_(
                "No expense pool data found for %(date)s. "
                "Please generate a snapshot first.",
                date=target_date,
            ))

        for line in self.invoice_line_ids.filtered(lambda l: l.display_type == 'product'):
            line.analytic_distribution = distribution
