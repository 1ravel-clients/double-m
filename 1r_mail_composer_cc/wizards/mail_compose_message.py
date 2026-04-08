from odoo import fields, models, tools


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    partner_cc_ids = fields.Many2many(
        'res.partner',
        'mail_compose_message_res_partner_cc_rel',
        'wizard_id', 'partner_id',
        string='Cc',
    )

    def _prepare_mail_values_rendered(self, res_ids):
        """Add email_cc from partner_cc_ids to the mail values."""
        results = super()._prepare_mail_values_rendered(res_ids)
        if self.partner_cc_ids:
            email_cc = ', '.join(
                tools.formataddr((p.name or '', p.email or ''))
                for p in self.partner_cc_ids
                if p.email
            )
            for res_id in res_ids:
                existing_cc = results[res_id].get('email_cc', '')
                if existing_cc:
                    results[res_id]['email_cc'] = f'{existing_cc}, {email_cc}'
                else:
                    results[res_id]['email_cc'] = email_cc
        return results
