from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'stock.location'
    _description = 'Stock Location'

    is_shopify_location = fields.Boolean("Shopify Location")
