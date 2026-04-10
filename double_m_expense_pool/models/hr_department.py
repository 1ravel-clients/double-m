from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )
    headcount_percentage = fields.Integer(
        string='Headcount %',
        compute='_compute_headcount_percentage',
    )

    def _compute_headcount_percentage(self):
        """Compute each department's share of total headcount.

        Only departments with an analytic account are in the pool.
        Uses the largest remainder method so percentages always sum
        to exactly 100%.
        """
        pool = self.search([('analytic_account_id', '!=', False)])
        total = sum(d.total_employee for d in pool)

        if not total:
            for dept in self:
                dept.headcount_percentage = 0
            return

        # Largest remainder method for exact 100%
        raw = {d.id: d.total_employee * 100 / total for d in pool}
        floored = {did: int(v) for did, v in raw.items()}
        remainder = {did: raw[did] - floored[did] for did in raw}
        diff = 100 - sum(floored.values())
        for did in sorted(remainder, key=remainder.get, reverse=True)[:diff]:
            floored[did] += 1

        for dept in self:
            dept.headcount_percentage = floored.get(dept.id, 0)
