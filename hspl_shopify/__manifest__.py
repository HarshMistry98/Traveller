{
    'name': "Shopify",

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
    'depends': ['base', 'sale', 'stock', 'website_sale', 'l10n_in'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'data/cron_jobs.xml',

        'wizards/operation.xml',

        'views/config.xml',
        'views/customerdetails.xml',
        'views/productdetails.xml',
        'views/ordersdetails.xml',
        'views/productdetailstemplate.xml',
        'views/webhooks.xml',

        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
# -*- coding: utf-8 -*-
