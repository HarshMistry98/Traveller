{
    'name': "harshexam",

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
    'depends': ['base', "sale", "purchase"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'report/report_invoice.xml',

        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/product_brand.xml',
        'views/product_template.xml',
        'views/product_brand.xml',
        'views/stock_picking.xml',
        'views/web_brand_view.xml',

        'views/purchase_menus.xml',

        'wizards/vendor_report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
# -*- coding: utf-8 -*-
