{
    'name': '1R - Sale Project Deferred Creation',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Defer project creation from SO confirmation to a manual wizard filtered by payment status',
    'author': '1Ravel',
    'website': 'https://1ravel.com',
    'depends': ['sale_project', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/create_project_wizard_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
