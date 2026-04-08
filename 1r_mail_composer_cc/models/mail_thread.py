from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_by_email_get_base_mail_values(self, message, recipients_data, additional_values=None):
        """Add email_cc from composer context to outgoing mail.mail values."""
        res = super()._notify_by_email_get_base_mail_values(
            message, recipients_data, additional_values=additional_values,
        )
        email_cc = self.env.context.get('composer_email_cc')
        if email_cc:
            existing_cc = res.get('email_cc', '')
            if existing_cc:
                res['email_cc'] = f'{existing_cc}, {email_cc}'
            else:
                res['email_cc'] = email_cc
        return res
