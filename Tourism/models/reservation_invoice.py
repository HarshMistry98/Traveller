from odoo import fields, models, api
from odoo.exceptions import UserError


class travel_reservation_invoice(models.Model):
    _name = 'travel.reservation_invoice'
    _description = 'All details regarding reservation booking is shown here'
    _inherit = "portal.mixin"
    _rec_name = "invoice_seq"

    invoice_seq = fields.Char(string='Invoice Sequence')

    customer_id = fields.Many2one(comodel_name="travel.customer_details", string="Customer")
    itinerary_id = fields.Many2one(comodel_name="travel.itinerary", string="Itinerary",
                                   domain="[('customer_ids','=',customer_id)]")

    agency_id = fields.Many2one(comodel_name="travel.agency", string="Agency",
                                domain="[('itinerary_ids', '=', itinerary_id)]")
    booking_id = fields.Many2one(comodel_name="travel.reservation_booking", string="Booking")
    payment_id = fields.Many2one(comodel_name="travel.customer_payment", string="Payment")

    discount_id = fields.Many2one(comodel_name="travel.offer_discount", string="Discount")

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, string='Currency')
    it_amount = fields.Monetary(currency_field='currency_id', compute='_compute_it_amount', string='Itinerary Amt.')
    tp_amount = fields.Monetary(currency_field='currency_id', compute='_compute_tp_amount', string='Transport Amt.')
    total_amount = fields.Float(string='Total Amount', store=1)

    due_date = fields.Date(string="Due Date")
    status = fields.Selection([
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ], string="Payment Status", default="unpaid", related="payment_id.payment_status")
    state = fields.Selection(
        [('customer', "Customer"), ('payment', "Payment"), ('booking', "Booking"), ('invoice', "Invoice")],
        default="invoice")

    transport_id = fields.Many2one("travel.transportation_flight", "Transport")


    # status = fields.Char(string="Status")

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

    @api.depends("transport_id")
    def _compute_tp_amount(self):
        for record in self:
            if record.transport_id:
                record.tp_amount = record.transport_id.price
            else:
                record.tp_amount = 0

    @api.onchange('tp_amount', "it_amount")
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.it_amount + record.tp_amount

    def send_invoice(self):
        for rec in self:
            if rec.status == "paid":
                rec.env.ref("Tourism.invoice_mail_template").send_mail(self.id)
                print("Invoice sent")
            else:
                print("Invoice not sent")
                raise UserError("Can't send mail and generate invoice for Payment Status: Unpaid")



    @api.model_create_multi
    def create(self, vals_list):
        records = super(travel_reservation_invoice, self).create(vals_list)
        for rec in records:
            seq = self.env['ir.sequence'].next_by_code('travel.reservation.invoice.seq')
            rec.invoice_seq = seq
        return records

    def write(self, vals):
        if not self.invoice_seq:
            seq = self.env['ir.sequence'].next_by_code('travel.reservation.invoice.seq')
            vals.update({
                'invoice_seq': seq
            })
        res = super(travel_reservation_invoice, self).write(vals)
        return res

    def _get_portal_return_action(self):
        """ Return the action used to display orders when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('Tourism.action_travel_reservation_invoice')

    def _compute_access_url(self):
        super()._compute_access_url()
        for inv in self:
            inv.access_url = f'/my/invoice/{inv.id}'
