from odoo import fields, models, api


class travel_transportation_road(models.Model):
    _name = 'travel.transportation_road'
    _description = 'All details regarding road are shown here'

    from_city = fields.Char(string="From City")
    to_city = fields.Char(string="To City")
    date = fields.Date(string="Date")
    travellers_adult = fields.Integer(string="Adult Traveller")
    travellers_child = fields.Integer(string="Child Traveller")
    travellers_handicapped = fields.Integer(string="Handicapped Traveller")