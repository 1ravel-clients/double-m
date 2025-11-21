from odoo import api, fields, models, _

class ContactLine(models.TransientModel):
    _name = 'contact.line'

    contact_id = fields.Many2one(comodel_name="res.partner", required=True, ondelete='cascade')
    wizard_id = fields.Many2one(comodel_name="contact.to.task.wizard", string="Wizard", required=True, ondelete='cascade')

class ContactToTaskTransferComfirmWizard(models.TransientModel):
    _name = 'contact.to.task.confirm.wizard'

    wizard_id = fields.Many2one(comodel_name="contact.to.task.wizard", string="Wizard", required=True, ondelete='cascade')
    message = fields.Char(readonly=1)

    def contact_to_task_confirm_action(self):
        return self.wizard_id.contact_to_task_action(check_exist=False)

class SuccessNotificationWizard(models.TransientModel):
    _name = 'success.notification.wizard'

    message = fields.Char(readonly=1)

class ContactToTaskTransferWizard(models.TransientModel):
    _name = 'contact.to.task.wizard'

    def _default_contact_ids(self):
        contact_ids = self._context.get('active_model') == 'res.partner' and self._context.get('active_ids') or []
        return [
            (0, 0, {'contact_id': contact.id})
            for contact in self.env['res.partner'].browse(contact_ids)
        ]

    project_id = fields.Many2one(string="Project", comodel_name="project.project")
    project_stage = fields.Many2one(string="Stage", comodel_name="project.task.type")
    date_deadline = fields.Date(string="Deadline")
    contact_ids = fields.One2many(comodel_name="contact.line", inverse_name="wizard_id", default=_default_contact_ids)

    def _check_contact_exist_in_project(self):
        self.ensure_one()
        existed_contact = []
        for contact in self.contact_ids.contact_id:
            if contact.id in self.project_id.tasks.mapped('contact_id.id'):
                existed_contact.append(contact.name)

        if len(existed_contact) > 0:
            msg = _(f"Currently these contact {', '.join(str(c) for c in existed_contact)} existed in the project {self.project_id.name}")
            return True, msg

        return False

    def open_confirmation_popup_wizard(self, msg, wizard_id):
        context = dict(self.env.context)
        context.update({
            'default_message': msg,
            'default_wizard_id': wizard_id,
            'confirm_action': True
        })
        return {
            'name': _('Confirm convert to tasks'),
            'view_mode': 'form',
            'res_model': 'contact.to.task.confirm.wizard',
            'views': [(self.env.ref('double_m_contacts.contact_to_task_wizard_confirm_view').id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    def open_success_notification_popup(self, msg):
        context = dict(self.env.context)
        context.update({
            'default_message': msg,
        })
        return {
            'name': _('Successfully imported'),
            'view_mode': 'form',
            'res_model': 'success.notification.wizard',
            'views': [(self.env.ref('double_m_contacts.notification_view').id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    def contact_to_task_action(self, check_exist=True):
        if check_exist:
            res = self._check_contact_exist_in_project()
            if res != False and res[0] == True:
                return self.open_confirmation_popup_wizard(msg=res[1], wizard_id=self.id)

        for contact in self.contact_ids:
            new_task = {
                'name': contact.contact_id.name,
                'project_id': self.project_id.id,
                'contact_id': contact.contact_id.id,
                'contact_phone': contact.contact_id.phone,
                'stage_id': self.project_stage.id,
                'description': contact.contact_id.comment,
                'date_deadline':self.date_deadline,
                'tag_ids': [],
                'contact_info_ids': []
            }

            # Sync tags from Contact -> Task
            for tag in contact.contact_id.category_id:
                exist_tag = self.env['project.tags'].sudo().search([('name', '=', tag.name)], limit=1)
                if exist_tag:
                    new_task['tag_ids'].append((4, exist_tag.id))
                else:
                    new_task['tag_ids'].append((0, 0, {
                        'name': tag.name
                    }))

            # Sync contact and address from Contact -> Task
            for rec in contact.contact_id.child_ids:
                new_task['contact_info_ids'].append((4, rec.id))

            self.env['project.task'].sudo().create(new_task)

        return self.open_success_notification_popup(f'{len(self.contact_ids)} records sucessfully imported')
