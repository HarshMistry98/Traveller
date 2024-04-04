from odoo import fields, models, api
import requests

class productsDetails(models.Model):
    _inherit = 'product.template'
    _description = 'Product Details'

    shopify_product_id = fields.Char("Shopify ID")

