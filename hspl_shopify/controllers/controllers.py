# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.tools import json


class ShopifyWebhooksController(http.Controller):

    @http.route(['/customers/update', '/customers/create'], type='json', methods=['POST'])
    def customer_create_or_update(self):
        if request.httprequest.method == 'POST':
            try:
                data = json.loads(request.httprequest.data)
                self.env['res.partner'].update_customers(data)
            except Exception as e:
                return {"error": str(e)}
        return {"success": True}

    @http.route(['/products/update', '/products/create'], type='json', methods=['POST'])
    def customer_create_or_update(self):
        if request.httprequest.method == 'POST':
            try:
                data = json.loads(request.httprequest.data)
                self.env['product.template'].update_products(data)
            except Exception as e:
                return {"error": str(e)}
        return {"success": True}

    @http.route('/orders/create', type='json', methods=['POST'])
    def customer_create_or_update(self):
        if request.httprequest.method == 'POST':
            try:
                data = json.loads(request.httprequest.data)
                self.env['sale.order'].update_orders(data)
            except Exception as e:
                return {"error": str(e)}
        return {"success": True}