/** @odoo-module **/
import { AnalyticDistribution } from "@analytic/components/analytic_distribution/analytic_distribution";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

patch(AnalyticDistribution.prototype, {
    setup() {
        super.setup();
        this.notification = useService("notification");
    },

    async onApplyExpensePool() {
        const moveId = this.props.record.model.root.resId;
        if (!moveId) {
            this.notification.add(
                _t("Save the bill before applying the expense pool."),
                { type: "warning" },
            );
            return;
        }
        const distribution = await this.orm.call(
            "account.move",
            "get_expense_pool_distribution",
            [moveId],
        );
        if (!distribution || !Object.keys(distribution).length) {
            this.notification.add(
                _t("No expense pool data for this period. Configure department analytic accounts (Employees > Expense Pool > Department Setup) and generate a snapshot."),
                { type: "warning" },
            );
            return;
        }
        await this.props.record.update({
            [this.props.name]: distribution,
            is_expense_pool_distributed: true,
        });
        await this.jsonToData(distribution);
    },
});
