from odoo import api, fields, models, _

class Task(models.Model):
    _inherit = 'project.task'

    def open_assign_deadline_to_task_wizard(self):
        context = dict(self.env.context)
        return {
            'name': _('Assign deadline to tasks'),
            'view_mode': 'form',
            'res_model': 'assign.deadline.to.task.wizard',
            'views': [(self.env.ref('double_m_task_assign_deadline.assign_deadline_to_task_wizard_form_view').id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
