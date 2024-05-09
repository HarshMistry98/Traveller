# -*- coding: utf-8 -*-
{
    'name': "Employee_Loan",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'payroll','portal','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/Security_access_file.xml',

        'data/ir_sequence.xml',

        'views/loans.xml',
        'views/schedule.xml',
        'views/employee_inherit.xml',
        # Start from here Apr 2 24
        'views/loan_menu_inherit.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/data_payroll.xml',
    ],
    'application': True,
}
