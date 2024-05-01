from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'product.product'
    _description = 'Product Product'

    brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")
