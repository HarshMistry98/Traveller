from odoo import fields, models, api
import requests

class productsDetails(models.Model):
    _inherit = 'product.product'
    _description = 'Product Details'

    shopify_product_id = fields.Char("Shopify Product ID")
    shopify_variant_id = fields.Char("Shopify Variant ID")
    # def update_products(self):
    #
    #     print("Product printed")
