from odoo import api, fields, models, _

class Partner(models.Model):
    _inherit = 'res.partner'

    pic = fields.Char(string="PIC")
    pic_position = fields.Char(string="PIC Position")
    pic_phone = fields.Char(string="PIC Phone")
    pic_email = fields.Char(string="PIC email address")
    is_main_contact = fields.Boolean(string="Main contact")
    current_user_id = fields.Many2one(comodel_name='res.users', compute="_compute_current_user_id", default=lambda self: self.env.user)
    current_user_country = fields.Selection(related="current_user_id.country")
    contact_phone_gcalls = fields.Char(string="Phone", compute="_compute_contact_phone_gcalls", inverse="_inverse_contact_phone_gcalls")

    @api.depends()
    def _compute_current_user_id(self):
        for rec in self:
            rec.current_user_id = self.env.user

    @api.depends('phone')
    def _compute_contact_phone_gcalls(self):
        for rec in self:
            rec.contact_phone_gcalls = rec.phone

    def _inverse_contact_phone_gcalls(self):
        for rec in self:
            rec.phone = rec.contact_phone_gcalls

    @api.onchange('company_type')
    def onchange_company_type(self):
        self.is_company = (self.company_type == 'company')
        self.is_main_contact = True if self.company_type == 'company' else False

    def open_contact_to_task_wizard(self):
        context = dict(self.env.context)
        return {
            'name': _('Convert to tasks'),
            'view_mode': 'form',
            'res_model': 'contact.to.task.wizard',
            'views': [(self.env.ref('double_m_contacts.contact_to_task_wizard_form_view').id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }


    def action_make_biz_call(self):
        # This funcion will be overided to be able to make call to Contact
        return
