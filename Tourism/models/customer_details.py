# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class travel_customer_details(models.Model):
    _name = 'travel.customer_details'
    _description = 'All customer details booked with our organizations.'
    _rec_name = "customer_seq"
    _rec_names_search = ['first_name', 'last_name', 'email']
    # _sql_constraints = [
    #     ('check_contact_length', "CHECK (LENGTH(contact) != 10)","Mobile number must be of length 10"),
    #     ('check_contact_numeric', "CHECK (contact ~ '^[0-9]+$')", "Mobile number must contain only numeric digits"),
    # ]

    customer_seq = fields.Char(string='Customer Sequence')

    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    itinerary_id = fields.Many2one(comodel_name="travel.itinerary", string="Itinerary")
    agency_id = fields.Many2one(
        comodel_name="travel.agency",
        string="Agency",
        domain="[('itinerary_ids', '=', itinerary_id)]"
    )
    contact = fields.Char(string='Contact')
    email = fields.Char(string="Email")
    state = fields.Selection(
        [('customer', "Customer"), ('payment', "Payment"), ('booking', "Booking"), ('invoice', "Invoice")],
        default="customer")

    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=', country_id)]")

    payment_ids = fields.One2many("travel.customer_payment", "customer_id")

    dp = fields.Image(string='Profile Image', max_width=128, max_height=128, attachment=True)

    # @api.constrains("contact")
    # def contact_10_digit(self):
    #     for rec in self:
    #         if not (len(rec.contact)==10 and rec.contact.isnumeric()):
    #             raise ValidationError("Enter a valid 10 digit contact number")
    @api.onchange('country_id')
    def onchange_country_id(self):
        """Update the state dropdown based on the selected country."""
        if self.country_id:
            return {'domain': {'state_id': [('country_id', '=', self.country_id.id)]}}
        else:
            return {'domain': {'state_id': []}}

    # @api.onchange('state_id')
    def onchange_state_id(self):
        """Update the city dropdown based on the selected state."""
        if self.state_id:
            return {'domain': {'city_id': [('state_id', '=', self.state_id.id)]}}
        else:
            return {'domain': {'city_id': []}}

    def next_payment(self):
        self.state = "payment"

    @api.model_create_multi
    def create(self, vals_list):
        records = super(travel_customer_details, self).create(vals_list)
        for rec in records:
            seq = self.env['ir.sequence'].next_by_code('travel.customer.details.seq')
            rec.customer_seq = seq
        return records

    def write(self, vals):
        if not self.customer_seq:
            seq = self.env['ir.sequence'].next_by_code('travel.customer.details.seq')
            vals.update({
                'customer_seq': seq
            })
        res = super(travel_customer_details, self).write(vals)
        return res

    def name_get(self):
        res = []
        for pays in self:
            if pays.first_name and pays.last_name:
                name = pays.customer_seq + " " + pays.first_name + " " + pays.last_name
            else:
                name = "--No name available--"
            res.append((pays.id, name))
        return res

    # @api.multi
    def action_view_customer_payment(self):
        if len(self.payment_ids) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Customer Payment',
                'res_model': 'travel.customer_payment',
                'view_mode': 'form',
                'res_id': self.payment_ids.id,
            }
        elif len(self.payment_ids) > 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Customer Payment',
                'res_model': 'travel.customer_payment',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', self.payment_ids.ids)],
        }
        else:
            # No records found
            raise UserError('No records found.')