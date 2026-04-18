/** @odoo-module **/
import { AnalyticDistribution } from "@analytic/components/analytic_distribution/analytic_distribution";
import { patch } from "@web/core/utils/patch";

patch(AnalyticDistribution.prototype, {
    /**
     * Fetch expense-pool ratios for the parent move's invoice_date
     * and load them into the analytic distribution popup.
     */
    async onApplyExpensePool() {
        const record = this.props.record;
        // Get the parent move id from the line record
        const moveId = record.data.move_id && record.data.move_id[0];
        if (!moveId) {
            return;
        }
        const distribution = await this.orm.call(
            "account.move",
            "get_expense_pool_distribution",
            [moveId],
        );
        if (distribution && Object.keys(distribution).length) {
            await this.props.record.update({ [this.props.name]: distribution });
            await this.jsonToData(distribution);
        }
    },
});
