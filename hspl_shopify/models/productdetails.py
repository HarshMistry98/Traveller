from odoo import fields, models, api
import requests

class productsDetails(models.Model):
    _inherit = 'product.product'
    _description = 'Product Details'

    is_shopify_variant = fields.Boolean(string="Shopify Variant")

    shopify_product_id = fields.Char("Shopify Product ID")
    shopify_variant_id = fields.Char("Shopify Variant ID")

    shopify_inventory_id = fields.Char("Shopify Inventory ID")

    def update_product_variants(self, product, product_id):
        '''Update product variants'''
        product_variant = self.search([('product_tmpl_id', '=', product_id.id)])
        variants = product.get('variants')
        if variants:
            for variant in variants:
                options = [variant.get(f'option{i}') for i in range(1, 4) if variant.get(f'option{i}')]
                for item in product_variant:
                    if item.product_template_attribute_value_ids:
                        list_values = [rec.name for rec in item.product_template_attribute_value_ids]
                        if set(options).issubset(set(list_values)):
                            item.is_shopify_variant = True
                            item.shopify_variant_id = variant.get('id')
                            item.shopify_product_id = variant.get('product_id')
                            item.shopify_inventory_id = variant.get('inventory_item_id')
                            item.barcode = variant.get('barcode')
                            item.weight = variant.get('weight')
                            item.lst_price = variant.get('price')

