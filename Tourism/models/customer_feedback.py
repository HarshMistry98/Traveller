# -*- coding: utf-8 -*-,

from odoo import models, fields, api


class travel_customer_feedback(models.Model):
    _name = 'travel.customer_feedback'
    _description = 'All customer feedback are stored here.'

    customer_id = fields.Many2one(comodel_name="travel.customer_details", string="Customer")
    itinerary_id = fields.Many2one(comodel_name="travel.itinerary", string="Itinerary")
    booking_id = fields.Many2one(comodel_name="travel.reservation_booking", string="Booking")
    suggestions = fields.Html(string='Suggestions')
    rating = fields.Selection([
        ('0', '0 Star'),
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars'),
        ('4', '4 Stars'),
        ('5', '5 Stars'),
    ], string="Satisfaction")