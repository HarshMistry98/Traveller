from odoo import fields, models, api


class ModelName(models.Model):
    _name = 'shopify.image'
    _description = 'Shopify Images'

    name = fields.Char()
    position = fields.Char()
    shopify_image_id = fields.Char()
    shopify_product_id = fields.Char()
    product_tmpl_id = fields.Many2one("product.template", string="Product Template")
    product_variant_id = fields.Many2many("product.product", string="Product Variants",
                                          domain="[('product_tmpl_id', '=', product_tmpl_id)]")
    image_1920 = fields.Image()
