# -*- coding: utf-8 -*-
# from odoo import http


# class TravelAndTourism(http.Controller):
#     @http.route('/travel_and__tourism/travel_and__tourism', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/travel_and__tourism/travel_and__tourism/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('travel_and__tourism.listing', {
#             'root': '/travel_and__tourism/travel_and__tourism',
#             'objects': http.request.env['travel_and__tourism.travel_and__tourism'].search([]),
#         })

#     @http.route('/travel_and__tourism/travel_and__tourism/objects/<model("travel_and__tourism.travel_and__tourism"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('travel_and__tourism.object', {
#             'object': obj
#         })
