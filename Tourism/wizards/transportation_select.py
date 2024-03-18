# models/wizards/transportation_selection.py

from odoo import models, fields, api
from odoo.exceptions import UserError


class TransportationSelection(models.TransientModel):
    _name = 'travel.transportation_selection'
    _description = 'Transportation Selection Wizard'

    mode_of_transport = fields.Selection([
        ('flight', 'Flight'),
        ('railway', 'Railway'),
        ('road', 'Road')
    ], string='Mode of Transport', default="flight")

    # @api.multi
    def action_confirm(self):
        for trans in self:
            if trans.mode_of_transport == 'flight':
                transport_action = self.env.ref('Tourism.action_travel_transportation_flight_form').read()[0]
            elif trans.mode_of_transport == 'railway':
                transport_action = self.env.ref('Tourism.action_travel_transportation_railway').read()[0]
            elif trans.mode_of_transport == 'road':
                transport_action = self.env.ref('Tourism.action_travel_transportation_road').read()[0]
            else:
                raise UserError("Select mode of transport")

            # transport_action.update({
            #     'target': 'current',
            #     'view_mode': 'form',
            # })
            return transport_action

        # Access the selected mode_of_transport value from the context
        # mode_of_transport = self.env.context.get('mode_of_transport')
        # print(mode_of_transport)
        # # Update the field in the current form view
        # self.env['travel.reservation_booking'].browse(self.env.context.get('active_id')).write(
        #     {'mode_of_transport': mode_of_transport})
        #
        # # Open the current form view
        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'travel.reservation_booking',
        #     'view_mode': 'form',
        #     'res_id': self.env.context.get('active_id'),
        #     'target': 'current',
        # }
