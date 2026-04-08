from markupsafe import Markup

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
        """Pass CC partner emails through context for the notification hook,
        and append CC info to the chatter message for audit."""
        if self.partner_cc_ids:
            email_cc = ', '.join(
                tools.formataddr((p.name or '', p.email or ''))
                for p in self.partner_cc_ids
                if p.email
            )
            self = self.with_context(composer_email_cc=email_cc)
        mails, messages = super()._action_send_mail_comment(res_ids)
        if self.partner_cc_ids:
            cc_entries = []
            for p in self.partner_cc_ids:
                if p.email:
                    cc_entries.append(f'{p.name or p.email} &lt;{p.email}&gt;')
            cc_line = Markup(
                '<p class="text-muted small mt-2 mb-0">'
                '<strong>CC:</strong> %s'
                '</p>'
            ) % Markup(', ').join(Markup(e) for e in cc_entries)
            for message in messages:
                message.sudo().write({'body': message.body + cc_line})
        return mails, messages
