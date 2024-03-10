# -*- coding: utf-8 -*-

from odoo import models, fields, api


class travel_customer_payment(models.Model):
    _name = 'travel.customer_payment'
    _description = 'All customer details booked with our organizations.'
    _rec_name = "payment_seq"

    payment_seq = fields.Char(string='Payment Sequence')

    customer_id = fields.Many2one(comodel_name="travel.customer_details", string="Customer")
    itinerary_id = fields.Many2one(comodel_name="travel.itinerary", string="Itinerary",
                                   domain="[('customer_ids','=',customer_id)]")
    agency_id = fields.Many2one(comodel_name="travel.agency", string="Agency",
                                domain="[('itinerary_ids', '=', itinerary_id)]")
    payment_date = fields.Date(string='Payment Date')
    amount = fields.Integer(string='Amount')
    payment_method = fields.Char(string='Payment Method')
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ], string="Payment Status", default="unpaid")
    state = fields.Selection(
        [('customer', "Customer"), ('payment', "Payment"), ('booking', "Booking"), ('invoice', "Invoice")],
        default="payment")

    @api.model_create_multi
    def create(self, vals_list):
        records = super(travel_customer_payment, self).create(vals_list)
        for rec in records:
            seq = self.env['ir.sequence'].next_by_code('travel.customer.payment.seq')
            rec.payment_seq = seq
        return records

    def write(self, vals):
        if not self.payment_seq:
            seq = self.env['ir.sequence'].next_by_code('travel.customer.payment.seq')
            vals.update({
                'payment_seq': seq
            })
        res = super(travel_customer_payment, self).write(vals)
        return res

    def action_view_booking(self):
        booking_action = self.env.ref('Tourism.action_travel_reservation_booking').read()[0]
        booking_action.update({
            'domain': [('customer_id', '=', self.id)],
        })
        return booking_action
