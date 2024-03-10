from odoo import fields, models, api
from odoo.exceptions import UserError


class travel_reservation_booking(models.Model):
    _name = 'travel.reservation_booking'
    _description = 'All details regarding reservation booking is shown here'
    _rec_name = "booking_seq"

    booking_seq = fields.Char(string='Booking Sequence')

    customer_id = fields.Many2one(comodel_name="travel.customer_details", string="Customer")
    itinerary_id = fields.Many2one(comodel_name="travel.itinerary", string="Itinerary", domain="[('customer_ids','=',customer_id)]")
    agency_id = fields.Many2one(comodel_name="travel.agency", string="Agency",domain="[('itinerary_ids', '=', itinerary_id)]")
    payment_id = fields.Many2one(comodel_name="travel.customer_payment", string="Payment")
    discount_id = fields.Many2one(comodel_name="travel.offer_discount", string="Discount")
    state = fields.Selection([('customer', "Customer"), ('payment', "Payment"), ('booking', "Booking"), ('invoice', "Invoice")], default="booking")


    @api.model_create_multi
    def create(self, vals_list):
        records = super(travel_reservation_booking, self).create(vals_list)
        for rec in records:
            seq = self.env['ir.sequence'].next_by_code('travel.reservation.booking.seq')
            rec.booking_seq = seq
        return records

    def write(self, vals):
        if not self.booking_seq:
            seq = self.env['ir.sequence'].next_by_code('travel.reservation.booking.seq')
            vals.update({
                'booking_seq': seq
            })
        res = super(travel_reservation_booking, self).write(vals)
        return res
    
    def unlink(self):
        if self.payment_id:
            raise UserError("You can't unlink this record")
        return super(travel_reservation_booking, self).unlink()


    def action_view_invoice(self):
        invoice_action = self.env.ref('Tourism.action_travel_reservation_invoice').read()[0]
        invoice_action.update({
            'domain': [('customer_id', '=', self.id)],
        })
        return invoice_action


    # @api.onchange("customer_id")
    # def set_itinerary(self):
    #     for record in self:
    #         if record.customer_id:
    #             record.itinerary_id=record.customer_id.itinerary_id