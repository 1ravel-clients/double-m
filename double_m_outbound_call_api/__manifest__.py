# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Outbound Call API',
    'version': '1.0',
    'sequence': 1,
    'category': '',
    'summary': 'API implementation to make outbound calls',
    'description': """
        This module contain API implementation to make outbound calls. \n
    """,
    'website': 'https://www.portcities.net',
    'author': 'Portcities Ltd.',
    'depends': ['base', 'project', 'web', 'double_m_contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/project_views.xml',
        'wizards/confirm_make_call.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'double_m_outbound_call_api/static/src/js/outbound_call.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
