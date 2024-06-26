from odoo import fields, models, api


class travel_transportation_flight(models.Model):
    _name = 'travel.transportation_flight'
    _description = 'All details regarding flights are shown here'
    _rec_name = "flight_seq"
    _inherit = "travel.transport"

    flight_seq = fields.Char(string='Flight Sequence')

    flight_class = fields.Selection([
        ('first_class', 'First Class'),
        ('business_class', 'Business Class'),
        ('economy_class', 'Economy Class'),
    ], string="Flight Class")

    price = fields.Monetary("Price", "currency_id",compute="_compute_price", default=0)
    
    need_transport=fields.Boolean("Need Transport", config_parameter="Tourism.need_transport")

    # print("need_transport------",need_transport)
    @api.model_create_multi
    def create(self, vals_list):
        records = super(travel_transportation_flight, self).create(vals_list)
        for rec in records:
            seq = self.env['ir.sequence'].next_by_code('travel.transport.flight.seq')
            rec.flight_seq = seq
        return records

    def write(self, vals):
        if not self.flight_seq:
            seq = self.env['ir.sequence'].next_by_code('travel.transport.flight.seq')
            vals.update({
                'flight_seq': seq
            })
        res = super(travel_transportation_flight, self).write(vals)
        return res

    @api.depends("travellers_adult", "flight_class")
    def _compute_price(self):
        for record in self:
            fare = 0
            if record.flight_class:
                if record.flight_class == "business_class":
                    fare = 7000 * record.travellers_adult
                if record.flight_class == "first_class":
                    fare = 5000 * record.travellers_adult
                if record.flight_class == "economy_class":
                    fare = 3000 * record.travellers_adult
            record.price = fare
