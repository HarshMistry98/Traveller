# -*- coding: utf-8 -*-
# from odoo import http


# class Shopify(http.Controller):
#     @http.route('/hspl_shopify/hspl_shopify', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hspl_shopify/hspl_shopify/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hspl_shopify.listing', {
#             'root': '/hspl_shopify/hspl_shopify',
#             'objects': http.request.env['hspl_shopify.hspl_shopify'].search([]),
#         })

#     @http.route('/hspl_shopify/hspl_shopify/objects/<model("hspl_shopify.hspl_shopify"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hspl_shopify.object', {
#             'object': obj
#         })
