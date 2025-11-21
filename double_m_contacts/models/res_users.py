from odoo import api, fields, models, _

class Users(models.Model):
    _inherit = 'res.users'

    extension = fields.Char(string="User extension")
    country = fields.Selection(string="Country", selection=[
        ('vietnam', 'Vietnam'),
        ('indo', 'Indonesia')
    ], required=True)
