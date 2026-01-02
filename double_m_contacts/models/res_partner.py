from odoo import api, fields, models, _
from odoo.tools import file_open
import base64

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

    def _get_default_image(self, is_company=False):
        """Get default image based on partner type"""
        try:
            if is_company:
                img_path = 'base/static/img/company_image.png'
            else:
                img_path = 'base/static/img/avatar_grey.png'
            
            with file_open(img_path, 'rb') as f:
                return base64.b64encode(f.read())
        except (FileNotFoundError, OSError):
            return False

    def _set_default_image(self):
        """Set default image if no image is provided"""
        for record in self:
            if not record.image_1920:
                default_image = self._get_default_image(record.is_company)
                if default_image:
                    # Use direct SQL update to avoid recursion
                    self.env.cr.execute(
                        "UPDATE res_partner SET image_1920 = %s WHERE id = %s",
                        (default_image, record.id)
                    )
                    # Invalidate cache to reflect the change
                    record.invalidate_recordset(['image_1920'])

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set default image"""
        # Set default image in vals_list if image_1920 is not provided
        for vals in vals_list:
            if 'image_1920' not in vals or not vals.get('image_1920'):
                is_company = vals.get('is_company', False)
                default_image = self._get_default_image(is_company)
                if default_image:
                    vals['image_1920'] = default_image
        
        return super().create(vals_list)

    def write(self, vals):
        """Override write to set default image if image_1920 is empty"""
        # Prevent recursion by checking context
        if self.env.context.get('skip_default_image'):
            return super().write(vals)
        
        # If image_1920 is being explicitly cleared, set default image
        if 'image_1920' in vals and not vals.get('image_1920'):
            # Determine is_company: use new value if provided, otherwise current value
            is_company = vals.get('is_company')
            if is_company is None:
                is_company = self[0].is_company if self else False
            
            default_image = self._get_default_image(is_company)
            if default_image:
                vals['image_1920'] = default_image
        
        result = super().write(vals)
        
        # After write, always check if image_1920 is empty and set default if needed
        # This handles cases where:
        # 1. is_company changed and image is empty
        # 2. Any other field changed and image is empty
        for record in self:
            if not record.image_1920:
                default_image = self._get_default_image(record.is_company)
                if default_image:
                    # Use context to prevent recursion
                    record.with_context(skip_default_image=True).write({'image_1920': default_image})
        
        return result
