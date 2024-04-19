from odoo import fields, models, api


class ProductImage(models.Model):
    _inherit = 'product.image'
    _description = 'Description'

    shopify_image_id = fields.Char("Shopify Image ID")
