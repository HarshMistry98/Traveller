# -*- coding: utf-8 -*-

from odoo import models, fields, api


class travel_agency(models.Model):
    _name = 'travel.agency'
    _description = 'Agency which are attached with the organization'
    _rec_name = "agency_name"

    itinerary_ids = fields.Many2many(comodel_name="travel.itinerary", string="Itinerary")
    # itinerary_id = fields.Many2one(comodel_name="travel.itinerary", string="Itinerary")

    agency_seq = fields.Char(string='Agency Sequence')

    agency_name = fields.Char(string='Name')
    # country = fields.Char(string='Country')
    # state = fields.Char(string='State')
    commission = fields.Integer(string='Commission')
    ratings = fields.Selection([
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars'),
        ('4', '4 Stars'),
        ('5', '5 Stars'),
    ], string="Ratings")
    contact = fields.Char(string='Contact')
    itinerary_count = fields.Integer(compute="_compute_itinerary_count")

    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=', country_id)]")

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
        records = super(travel_agency, self).create(vals_list)
        for rec in records:
            seq = self.env['ir.sequence'].next_by_code('travel.agency.seq')
            rec.agency_seq = seq
        return records

    def write(self, vals):
        if not self.agency_seq:
            seq = self.env['ir.sequence'].next_by_code('travel.agency.seq')
            vals.update({
                'agency_seq': seq
            })
        res = super(travel_agency, self).write(vals)
        return res

    @api.depends('itinerary_ids')
    def _compute_itinerary_count(self):
        for record in self:
            record.itinerary_count = len(record.itinerary_ids)

