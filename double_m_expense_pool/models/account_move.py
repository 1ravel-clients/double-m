from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def get_expense_pool_distribution(self, move_id):
        """Return the expense-pool analytic distribution for *move_id*'s date.

        Called via RPC from the analytic distribution popup widget.
        """
        move = self.browse(move_id)
        target_date = move.invoice_date or fields.Date.context_today(self)
        return self.env['expense.pool.snapshot'].get_distribution_for_date(target_date)
