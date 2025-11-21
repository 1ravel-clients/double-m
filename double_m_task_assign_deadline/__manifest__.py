# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Double M task customization',
    'version': '1.0',
    'sequence': 1,
    'category': '',
    'summary': 'Add server action to assign deadline for tasks',
    'description': """
        - This module add server action to assign deadline for tasks. \n
    """,
    'website': 'https://www.portcities.net',
    'author': 'Portcities Ltd.',
    'depends': ['project'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/wizard_assign_deadline.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
