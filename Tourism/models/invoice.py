from odoo import fields, models, api


class Invoice(models.Model):
    _description = 'Invoice'
    _inherit = 'account.move'

    name = fields.Char()
    itinerary_id = fields.Many2one(comodel_name="travel.itinerary", string="Itinerary")
    agency_id = fields.Many2one(
        comodel_name="travel.agency",
        string="Agency",
        domain="[('itinerary_ids', '=', itinerary_id)]"
    )