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

    flight_transport_id = fields.Many2one("travel.transportation_flight", "Transport")
    railway_transport_id = fields.Many2one("travel.transportation_railway", "Transport")
    road_transport_id = fields.Many2one("travel.transportation_road", "Transport")

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        readonly=True,
        default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
    )
    it_amount = fields.Monetary(currency_field='currency_id',compute="_compute_it_amount", string='Itinerary Amt.')

    flight_tp_amount = fields.Monetary(currency_field='currency_id', related="flight_transport_id.price", string='Transport Amt.', default=0)
    railway_tp_amount = fields.Monetary(currency_field='currency_id', related="railway_transport_id.price", string='Transport Amt.')
    road_tp_amount = fields.Monetary(currency_field='currency_id', related="road_transport_id.price", string='Transport Amt.')

    total_amount = fields.Monetary(currency_field='currency_id',string='Total Amount', store=1)

    mode_of_transport = fields.Selection([
        ('flight', 'Flight'),
        ('railway', 'Railway'),
        ('road', 'Road')
    ], string='Mode of Transport', default="flight")
    
    invoice_ids = fields.One2many("travel.reservation_invoice", "booking_id")


    # mode_of_transport = fields.Char("Mode")

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

    @api.depends('itinerary_id', 'discount_id')
    def _compute_it_amount(self):
        for record in self:
            if record.itinerary_id and record.discount_id:
                price = record.itinerary_id.price
                discount_percentage = record.discount_id.discount_percentage
                discounted_price = price - (price * discount_percentage / 100)
                record.it_amount = discounted_price
            else:
                record.it_amount = record.itinerary_id.price

    @api.onchange('flight_tp_amount', "it_amount")
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.it_amount + record.flight_tp_amount

    def action_view_invoice(self):
        if len(self.invoice_ids) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Reservation Invoice',
                'res_model': 'travel.reservation_invoice',
                'view_mode': 'form',
                'res_id': self.invoice_ids.id,
            }
        elif len(self.invoice_ids) > 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Reservation Invoice',
                'res_model': 'travel.reservation_invoice',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.invoice_ids.ids)],
        }
        else:
            # No records found
            raise UserError('No records found.')

    def action_select_transportation(self):
        return {
            'name': 'Transportation Selection',
            'type': 'ir.actions.act_window',
            'res_model': 'travel.transportation_selection',
            'view_mode': 'form',
            'view_id': self.env.ref('Tourism.view_transportation_selection_form').id,
            'target': 'new',
        }



    # @api.onchange("customer_id")
    # def set_itinerary(self):
    #     for record in self:
    #         if record.customer_id:
    #             record.itinerary_id=record.customer_id.itinerary_id