from odoo import api, fields, models, _

class TaskLine(models.TransientModel):
    _name = 'task.line'

    task_id = fields.Many2one(comodel_name="project.task", required=True, ondelete='cascade')
    wizard_id = fields.Many2one(comodel_name="assign.deadline.to.task.wizard", string="Wizard", required=True, ondelete='cascade')

class AssignDeadlinetoTaskWizard(models.TransientModel):
    _name = 'assign.deadline.to.task.wizard'

    def _default_task_ids(self):
        task_ids = self._context.get('active_model') == 'project.task' and self._context.get('active_ids') or []
        return [
            (0, 0, {'task_id': task.id})
            for task in self.env['project.task'].browse(task_ids)
        ]

    date_deadline = fields.Date(string="Deadline")
    task_ids = fields.One2many(comodel_name="task.line", inverse_name="wizard_id", default=_default_task_ids)

    def assign_deadline_to_task_action(self):
        for task_line in self.task_ids:
            task_id = task_line.task_id
            task_id.write({
                'date_deadline': self.date_deadline
            })
