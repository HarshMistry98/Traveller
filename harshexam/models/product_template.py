from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template'

    brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")
