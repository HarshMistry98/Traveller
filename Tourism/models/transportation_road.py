from odoo import fields, models, api


class travel_transportation_road(models.Model):
    _name = 'travel.transportation_road'
    _description = 'All details regarding road are shown here'
    _rec_name = 'road_seq'
    _inherit = "travel.transport"

    road_seq = fields.Char(string='Road Sequence')

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        readonly=True,
        default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
    )


    @api.model_create_multi
    def create(self, vals_list):
        records = super(travel_transportation_road, self).create(vals_list)
        for rec in records:
            seq = self.env['ir.sequence'].next_by_code('travel.transport.road.seq')
            rec.road_seq = seq
        return records

    def write(self, vals):
        if not self.road_seq:
            seq = self.env['ir.sequence'].next_by_code('travel.transport.road.seq')
            vals.update({
                'road_seq': seq
            })
        res = super(travel_transportation_road, self).write(vals)
        return res
