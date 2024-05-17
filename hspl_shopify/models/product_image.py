from odoo import fields, models, api


class ProductImage(models.Model):
    _inherit = 'product.image'
    _description = 'Description'

    shopify_image_id = fields.Char("Shopify Image ID")
    shopify_image_position = fields.Integer("Shopify Image Position")

    # default = "_get_default_shopify_image_id"
    # @api.depends('product_tmpl_id')
    # def _get_default_shopify_image_id(self):
    #     for record in self:
    #         image = self.env['product.image'].search(
    #             [('product_tmpl_id', '=', record.product_tmpl_id.id),
    #              ('sequence', '=', 1)], limit=1)
    #         record.shopify_variant_image_id = image.shopify_image_id if image else False




