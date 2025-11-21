import phonenumbers

from odoo.exceptions import ValidationError

from odoo import api, fields, models, _
from ..helpers.biz_api import BizAPI

class Partner(models.Model):
    _inherit = 'res.partner'

    def action_make_biz_call(self):
        phone_number = self.phone
        if not phone_number:
            raise ValidationError('Phone number has not been set. Please fill in the phone number.')

        try:
            format_phone_number = phonenumbers.parse(phone_number, None)
            e164_phone_number = str(phonenumbers.format_number(format_phone_number, phonenumbers.PhoneNumberFormat.E164))

            context = dict(self.env.context)
            context.update({
                'default_phone_number': e164_phone_number,
                'default_message': f"You will make a call to this number {e164_phone_number}"
            })
            return {
                'name': _('Confirm make a call'),
                'view_mode': 'form',
                'res_model': 'confirm.make.call.wizard',
                'views': [(self.env.ref('double_m_outbound_call_api.confirm_make_call_wizard_form_view').id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': context,
            }

        except phonenumbers.NumberParseException:
            raise ValidationError('The phone number may have incorrect format. It should follow E164 format, eg. +84902492')
