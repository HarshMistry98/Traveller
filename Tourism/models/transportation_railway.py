from odoo import fields, models, api


class travel_transportation_railway(models.Model):
    _name = 'travel.transportation_railway'
    _description = 'All details regarding railway are shown here'
    _rec_name = "railway_seq"
    _inherit = "travel.transport"

    railway_seq = fields.Char(string='Railway Sequence')

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


    @api.model_create_multi
    def create(self, vals_list):
        records = super(travel_transportation_railway, self).create(vals_list)
        for rec in records:
            seq = self.env['ir.sequence'].next_by_code('travel.transport.railway.seq')
            rec.railway_seq = seq
        return records

    def write(self, vals):
        if not self.railway_seq:
            seq = self.env['ir.sequence'].next_by_code('travel.transport.railway.seq')
            vals.update({
                'railway_seq': seq
            })
        res = super(travel_transportation_railway, self).write(vals)
        return res
