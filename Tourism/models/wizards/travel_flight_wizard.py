# models/wizards/travel_flight_wizard.py

from odoo import models, fields


class TravelFlightWizard(models.TransientModel):
    _name = 'travel.flight.wizard'
    _description = 'Flight Wizard'

    flight_number = fields.Char(string='Flight Number')
    departure_city = fields.Char(string='Departure City')
    arrival_city = fields.Char(string='Arrival City')
    departure_time = fields.Datetime(string='Departure Time')
    arrival_time = fields.Datetime(string='Arrival Time')
    # Add more fields as needed
