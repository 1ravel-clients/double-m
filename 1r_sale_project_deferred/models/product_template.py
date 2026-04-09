from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('project_id', 'project_template_id')
    def _check_project_and_template(self):
        """Allow project_template_id when service_tracking='no' (deferred creation).

        The native constraint forbids setting project_template_id when
        service_tracking is 'no'. We allow this combination so the template
        can be used later for manual project creation from the SO wizard.
        """
        for tmpl in self:
            # Allow: service_tracking='no' + project_template_id (no project_id)
            if tmpl.service_tracking == 'no' and tmpl.project_template_id and not tmpl.project_id:
                continue
            super(ProductTemplate, tmpl)._check_project_and_template()

    @api.onchange('service_tracking')
    def _onchange_service_tracking(self):
        """Keep project_template_id when switching to 'Nothing'.

        The native onchange clears both project_id and project_template_id
        when service_tracking is set to 'no'. We preserve project_template_id
        for deferred project creation.
        """
        if self.service_tracking == 'no':
            self.project_id = False
            # Keep project_template_id for deferred creation
            return
        super()._onchange_service_tracking()
