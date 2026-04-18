from odoo import api, fields, models


class ExpensePoolSnapshot(models.Model):
    _name = 'expense.pool.snapshot'
    _description = 'Expense Pool Monthly Snapshot'
    _order = 'date desc, department_id'
    _rec_name = 'department_id'

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        ondelete='cascade',
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        required=True,
    )
    date = fields.Date(
        string='Period',
        required=True,
        help='First day of the month this snapshot represents.',
    )
    headcount = fields.Integer(
        string='Headcount',
    )
    percentage = fields.Float(
        string='Weight %',
        digits=(5, 2),
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    _unique_dept_date = models.Constraint(
        'unique(department_id, date)',
        'Only one snapshot per department per month.',
    )

    # ------------------------------------------------------------------
    # Cron
    # ------------------------------------------------------------------

    @api.model
    def _cron_create_monthly_snapshot(self):
        """Called by the scheduled action on the 1st of each month."""
        today = fields.Date.context_today(self)
        self.create_snapshot_for_date(today)

    # ------------------------------------------------------------------
    # Snapshot generation
    # ------------------------------------------------------------------

    @api.model
    def create_snapshot_for_date(self, target_date=None):
        """Create (or update) snapshot records for *target_date*'s month.

        Can be called manually to back-fill past months or regenerate
        the current month.
        """
        if target_date is None:
            target_date = fields.Date.context_today(self)
        first_of_month = target_date.replace(day=1)

        departments = self.env['hr.department'].search([
            ('analytic_account_id', '!=', False),
        ])
        if not departments:
            return

        # Gather headcount per department
        employee_data = self.env['hr.employee'].sudo()._read_group(
            [('department_id', 'in', departments.ids)],
            ['department_id'],
            ['__count'],
        )
        hc_map = {dept.id: count for dept, count in employee_data}
        total = sum(hc_map.values())

        # Largest-remainder method so percentages sum to exactly 100
        if total:
            raw = {d.id: hc_map.get(d.id, 0) * 100 / total for d in departments}
        else:
            raw = {d.id: 0 for d in departments}
        floored = {did: int(v) for did, v in raw.items()}
        remainder = {did: raw[did] - floored[did] for did in raw}
        diff = 100 - sum(floored.values())
        for did in sorted(remainder, key=remainder.get, reverse=True)[:diff]:
            floored[did] += 1

        # Create or update records
        for dept in departments:
            existing = self.search([
                ('department_id', '=', dept.id),
                ('date', '=', first_of_month),
            ], limit=1)
            vals = {
                'department_id': dept.id,
                'analytic_account_id': dept.analytic_account_id.id,
                'date': first_of_month,
                'headcount': hc_map.get(dept.id, 0),
                'percentage': floored.get(dept.id, 0),
                'company_id': dept.company_id.id or self.env.company.id,
            }
            if existing:
                existing.write(vals)
            else:
                self.create(vals)

    # ------------------------------------------------------------------
    # Distribution helper (used by vendor-bill button)
    # ------------------------------------------------------------------

    @api.model
    def get_distribution_for_date(self, target_date):
        """Return analytic distribution dict for a given date.

        Format: ``{str(analytic_account_id): percentage, ...}``
        Falls back to a live computation when no snapshot exists for the
        requested month.
        """
        first_of_month = target_date.replace(day=1)
        snapshots = self.search([('date', '=', first_of_month)])
        if snapshots:
            return {
                str(s.analytic_account_id.id): s.percentage
                for s in snapshots
                if s.analytic_account_id
            }
        # Fallback: compute from current headcount
        departments = self.env['hr.department'].search([
            ('analytic_account_id', '!=', False),
        ])
        if not departments:
            return {}
        total = sum(d.total_employee for d in departments)
        if not total:
            return {}
        raw = {d.id: d.total_employee * 100 / total for d in departments}
        floored = {did: int(v) for did, v in raw.items()}
        remainder = {did: raw[did] - floored[did] for did in raw}
        diff = 100 - sum(floored.values())
        for did in sorted(remainder, key=remainder.get, reverse=True)[:diff]:
            floored[did] += 1
        return {
            str(d.analytic_account_id.id): floored[d.id]
            for d in departments
        }
