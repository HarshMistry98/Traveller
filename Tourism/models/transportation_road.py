from odoo import fields, models, api


class travel_transportation_road(models.Model):
    _name = 'travel.transportation_road'
    _description = 'All details regarding road are shown here'
    _rec_name = 'road_seq'

    road_seq = fields.Char(string='Road Sequence')

    from_city = fields.Char(string="From City")
    to_city = fields.Char(string="To City")
    date = fields.Date(string="Date")
    travellers_adult = fields.Integer(string="Adult Traveller")
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        readonly=True,
        default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
    )
    price = fields.Monetary("Price", "currency_id")


    @api.model_create_multi
    def create(self, vals_list):
        records = super(travel_transportation_road, self).create(vals_list)
        for rec in records:
            seq = self.env['ir.sequence'].next_by_code('travel.customer.details.seq')
            rec.road_seq = seq
        return records

    def write(self, vals):
        if not self.road_seq:
            seq = self.env['ir.sequence'].next_by_code('travel.customer.details.seq')
            vals.update({
                'road_seq': seq
            })
        res = super(travel_transportation_road, self).write(vals)
        return res
