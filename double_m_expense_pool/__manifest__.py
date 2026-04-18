{
    'name': 'Double M - Expense Pool Allocation',
    'version': '19.0.2.0.0',
    'category': 'Human Resources',
    'summary': 'Allocate general expenses across departments by headcount percentage with monthly snapshots',
    'author': '1Ravel',
    'depends': ['hr', 'account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/hr_department_views.xml',
        'views/expense_pool_snapshot_views.xml',
        'views/account_move_views.xml',
        'views/hr_menus.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
