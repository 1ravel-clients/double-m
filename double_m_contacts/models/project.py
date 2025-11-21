from odoo import api, fields, models, _

class Task(models.Model):
    _inherit = 'project.task'

    current_user_id = fields.Many2one(comodel_name='res.users', compute="_compute_current_user_id", default=lambda self: self.env.user)
    current_user_country = fields.Selection(related="current_user_id.country")
    contact_phone_gcalls = fields.Char(string="Contact Phone", compute="_compute_contact_phone_gcalls", inverse="_inverse_contact_phone_gcalls")
    contact_id = fields.Many2one(string="Contact", comodel_name="res.partner")
    contact_phone = fields.Char()
    contact_info_ids = fields.Many2many(comodel_name="res.partner", column1='task_id',column2='contact_id')

    @api.depends()
    def _compute_current_user_id(self):
        for rec in self:
            rec.current_user_id = self.env.user

    @api.depends('contact_phone')
    def _compute_contact_phone_gcalls(self):
        for rec in self:
            rec.contact_phone_gcalls = rec.contact_phone

    def _inverse_contact_phone_gcalls(self):
        for rec in self:
            rec.contact_phone = rec.contact_phone_gcalls

    @api.onchange('contact_id')
    def onchange_contact_id(self):
        if self.contact_id:
            self.contact_phone = self.contact_id.phone
            self.description = self.contact_id.comment
            self.contact_info_ids = self.contact_id.child_ids
            self.tag_ids = self.env['project.tags']
            for tag in self.contact_id.category_id:
                exist_tag = self.env['project.tags'].sudo().search([('name', '=', tag.name)], limit=1)
                if exist_tag:
                    self.tag_ids |= exist_tag
                else:
                    new_tag = self.env['project.tags'].sudo().create({
                        'name': tag.name
                    })
                    self.tag_ids |= new_tag
        else:
            self.contact_phone = None
            self.description = None
            self.tag_ids = None
