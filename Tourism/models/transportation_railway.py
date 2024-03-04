from odoo import fields, models, api


class travel_transportation_railway(models.Model):
    _name = 'travel.transportation_railway'
    _description = 'All details regarding railway are shown here'

    from_city = fields.Char(string="From City")
    to_city = fields.Char(string="To City")
    date = fields.Date(string="Date")
    travellers_adult = fields.Integer(string="Adult Traveller")
    travellers_child = fields.Integer(string="Child Traveller")
    travellers_handicapped = fields.Integer(string="Handicapped Traveller")
    railway_class = fields.Selection([
        ('Sleeper_Class', 'Sleeper Class'),
        ('AC_3_tier_Class', 'AC 3 tier Class'),
        ('AC_3_economy Class', 'AC 3 economy Class'),
        ('AC_2_tier_Class', 'AC 2 tier Class'),
        ('1A_Class', '1A Class'),
        ('First_Class_Class', 'First Class Class'),
        ('Executive_Chair_car_Class', 'Executive Chair car Class'),
        ('Second_Sitting_Clas_', 'Second Sitting Class'),
    ], string="Railway Class")