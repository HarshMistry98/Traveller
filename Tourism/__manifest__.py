{
    'name': "Tourism",

    'summary': """
        Module for Travel and Tourism Management""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Harsh Mistry",
    'website': "www.google.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'data/ir_sequence.xml',

        'views/wizards/transportation_select.xml',
        'views/wizards/travel_flight_wizard_views.xml',

        'views/actions.xml',
        'views/itinerary.xml',
        'views/agency.xml',
        'views/customer_details.xml',
        'views/customer_payment.xml',
        'views/customer_feedback.xml',
        'views/product.xml',
        'views/transportation_flight.xml',
        'views/transportation_railway.xml',
        'views/transportation_road.xml',
        'views/offer_discount.xml',
        'views/reservation_booking.xml',
        'views/reservation_invoice.xml',
        'views/invoice.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
# -*- coding: utf-8 -*-
