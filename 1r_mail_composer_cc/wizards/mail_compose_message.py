from odoo import fields, models, tools


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    partner_cc_ids = fields.Many2many(
        'res.partner',
        'mail_compose_message_res_partner_cc_rel',
        'wizard_id', 'partner_id',
        string='Cc',
    )

    def _action_send_mail_comment(self, res_ids):
        """Pass CC partner emails through context for the notification hook."""
        if self.partner_cc_ids:
            email_cc = ', '.join(
                tools.formataddr((p.name or '', p.email or ''))
                for p in self.partner_cc_ids
                if p.email
            )
            self = self.with_context(composer_email_cc=email_cc)
        return super()._action_send_mail_comment(res_ids)
