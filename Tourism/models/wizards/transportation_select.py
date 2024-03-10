# models/wizards/transportation_selection.py

from odoo import models, fields, api


class TransportationSelection(models.TransientModel):
    _name = 'travel.transportation.selection'
    _description = 'Transportation Selection Wizard'

    flight_selected = fields.Boolean(string='Flight')
    railway_selected = fields.Boolean(string='Railway')
    road_selected = fields.Boolean(string='Road')

    # @api.multi
    def action_confirm(self):
        transport_action = self.env.ref('Tourism.action_travel_flight_wizard').read()[0]
        return transport_action
