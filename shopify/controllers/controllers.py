# -*- coding: utf-8 -*-
# from odoo import http


# class Shopify(http.Controller):
#     @http.route('/shopify/shopify', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/shopify/shopify/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('shopify.listing', {
#             'root': '/shopify/shopify',
#             'objects': http.request.env['shopify.shopify'].search([]),
#         })

#     @http.route('/shopify/shopify/objects/<model("shopify.shopify"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shopify.object', {
#             'object': obj
#         })
