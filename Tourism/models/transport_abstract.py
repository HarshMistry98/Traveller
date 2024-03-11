from odoo import fields, models, api


class ModelName(models.AbstractModel):
    _name = 'travel.transport'
    _description = 'Abstract model for Transportation'

    name = fields.Char()

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
