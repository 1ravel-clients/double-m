# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Double M contacts customization',
    'version': '1.0',
    'sequence': 1,
    'category': '',
    'summary': 'Contact module customization',
    'description': """
        - This module customizes res.partner model. \n
        - Convert contact info to task model. \n
    """,
    'website': 'https://www.portcities.net',
    'author': 'Portcities Ltd.',
    'depends': ['base', 'contacts', 'project', 'sms'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/contact_to_task_transfer.xml',
        'views/res_partner_views.xml',
        'views/project_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
