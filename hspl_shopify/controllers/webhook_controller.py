import json

from odoo import http
from odoo.http import request


class ShopifyWebhooksController(http.Controller):

    @http.route(['/shopify/webhook/<string:webhook_for>/<string:webhook_action>'], type="http", auth="public",
                website=True, method=['POST'],
                csrf=False)
    def handle_webhook(self, webhook_for, webhook_action):
        if request.httprequest.method == 'POST':
            try:
                data = json.loads(request.httprequest.data)
                getattr(self, f'shopify_webhook_{webhook_for}_{webhook_action}')(data)
            except Exception as e:
                raise e

    def shopify_webhook_customers_create(self, data):
        request.env['res.partner'].update_customers(response_data=data)

    def shopify_webhook_customers_update(self, data):
        request.env['res.partner'].update_customers(response_data=data)

    def shopify_webhook_products_create(self, data):
        request.env['product.template'].update_products(response_data=data)

    def shopify_webhook_products_update(self, data):
        request.env['product.template'].update_products(response_data=data)

    def shopify_webhook_orders_create(self, data):
        request.env['sale.order'].update_orders(response_data=data)

    def shopify_webhook_orderts_updated(self, data):
        request.env['sale.order'].update_orders(response_data=data)
