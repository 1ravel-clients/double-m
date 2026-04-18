/** @odoo-module **/
import { AnalyticDistribution } from "@analytic/components/analytic_distribution/analytic_distribution";
import { patch } from "@web/core/utils/patch";

patch(AnalyticDistribution.prototype, {
    /**
     * Fetch expense-pool ratios for the parent move's invoice_date
     * and load them into the analytic distribution popup.
     */
    async onApplyExpensePool() {
        // The widget lives on an invoice line inside a one2many;
        // model.root is the parent form record (account.move).
        const moveId = this.props.record.model.root.resId;
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
