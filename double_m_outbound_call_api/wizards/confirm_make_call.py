from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from ..helpers.biz_api import BizAPI


class ConfirmMakeCallWizard(models.TransientModel):
    _name = "confirm.make.call.wizard"

    phone_number = fields.Char(readonly=True)
    message = fields.Char(readonly=True)

    def make_call(self):
        extension = self.env.user.extension
        if not extension:
            raise ValidationError('User extension has not been configured yet. Please set user extension to be able to make call.')

        return BizAPI.make_call(self.phone_number, extension)
