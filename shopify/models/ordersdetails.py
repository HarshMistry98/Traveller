from odoo import fields, models, api
import requests

class ordersDetails(models.Model):
    _inherit = 'sale.order'
    _description = 'Order Details'

    shopify_orders_id = fields.Char("Shopify ID")
    def update_orders(self):

        print("Orders printed")
