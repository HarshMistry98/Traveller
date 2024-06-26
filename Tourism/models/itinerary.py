# -*- coding: utf-8 -*-

from odoo import models, fields, api


class travel_itinerary(models.Model):
    _name = 'travel.itinerary'
    _description = 'All itinerary details will be shown here'
    _rec_name = "itinerary_name"
    _inherit = 'mail.thread'

    # Other fields in your model...

    agency_ids = fields.Many2many(comodel_name="travel.agency", string="Agency")
    customer_ids = fields.One2many(comodel_name="travel.customer_details", inverse_name="itinerary_id",
                                   string="Customers", tracking=1)
    # agency_ids = fields.One2many(comodel_name="travel.agency", inverse_name="itinerary_id", string="Agencies")

    itinerary_seq = fields.Char(string='Itinerary Sequence')

    itinerary_name = fields.Char(string='Itinerary')
    persons = fields.Integer(string='Persons')
    # price = fields.Integer(string='Price')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        readonly=True,
        default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
    )
    price = fields.Monetary("Price", "currency_id")
    days = fields.Integer(string='Days')
    nights = fields.Integer(string='Nights')
    date_availability = fields.Date(string='Date Availability')
    is_active = fields.Boolean(string='Active', tracking=1)
    rating = fields.Float("Rating", default=4.0)


    agency_count = fields.Integer(compute="_compute_agency_count")
    customer_count = fields.Integer(compute="_compute_customer_count")

    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=', country_id)]")

    photo = fields.Image(string='Image', style="height: 160px; width: 320px;", attachment=True)

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

    @api.model_create_multi
    def create(self, vals_list):
        records = super(travel_itinerary, self).create(vals_list)
        for rec in records:
            seq = self.env['ir.sequence'].next_by_code('travel.itinerary.seq')
            rec.itinerary_seq = seq
        return records

    def write(self, vals):
        if not self.itinerary_seq:
            seq = self.env['ir.sequence'].next_by_code('travel.itinerary.seq')
            vals.update({
                'itinerary_seq': seq
            })
        res = super(travel_itinerary, self).write(vals)
        return res

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        # if default:
        #     default.update({"hotel_name": self.hotel_name + "(Copy)"})
        # else:
        #     default = {"hotel_name": self.hotel_name + "(Copy)"}
        res = super(travel_itinerary, self).copy(default=default)
        res.itinerary_name = self.itinerary_name + "(Copy)"
        return res

    @api.depends('agency_ids')
    def _compute_agency_count(self):
        for record in self:
            record.agency_count = len(record.agency_ids)

    @api.depends('customer_ids')
    def _compute_customer_count(self):
        for record in self:
            record.customer_count = len(record.customer_ids)

    def action_agency(self):
        agency_action = self.env.ref('Tourism.action_travel_agency').read()[0]
        agency_action.update({
            'domain': [('itinerary_ids', '=', self.id)],
        })
        return agency_action

    def action_customer(self):
        print(self.env.ref('Tourism.action_travel_customer_details').read())

        agency_action = self.env.ref('Tourism.action_travel_customer_details').read()[0]
        agency_action.update({
            'domain': [('itinerary_id', '=', self.id)],
        })
        return agency_action


