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


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_expense_pool_distributed = fields.Boolean(
        string='Expense Pool Managed',
        default=False,
        copy=False,
        help="When True, the analytic distribution on this line is treated as "
             "expense-pool managed: the monthly cron will refresh it from each "
             "month's snapshot whenever this line is part of a deferred-expense "
             "entry.",
    )

    @api.model
    def _get_deferred_lines_values(self, account_id, balance, ref, analytic_distribution, line=None):
        vals = super()._get_deferred_lines_values(account_id, balance, ref, analytic_distribution, line)
        if line is not None:
            flag = (
                line.get('is_expense_pool_distributed')
                if isinstance(line, dict)
                else line.is_expense_pool_distributed
            )
            if flag:
                vals['is_expense_pool_distributed'] = True
        return vals
