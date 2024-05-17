import base64

from odoo import fields, models, api
import requests


class productsDetails(models.Model):
    _inherit = 'product.product'
    _description = 'Product Details'

    is_shopify_variant = fields.Boolean(string="Shopify Variant")

    shopify_product_id = fields.Char("Shopify Product ID")
    shopify_variant_id = fields.Char("Shopify Variant ID")

    shopify_inventory_id = fields.Char("Shopify Inventory ID")
    shopify_variant_image_id = fields.Char("Shopify Variant Image ID", default="_get_shopify_product_image_id")

    @api.depends('product_tmpl_id')
    def _get_shopify_product_image_id(self):
        for record in self:
            record.shopify_variant_image_id = self.product_tmpl_id.shopify_product_image_id
    def select_variant_image(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Select Image',
            'res_model': 'product_variant.image',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'current_product_tmpl_id': self.product_tmpl_id.id,
                        'current_product_id': self.id,
                        'shopify_variant_image_id': self.shopify_variant_image_id},
        }
        print("action", action)
        return action

    def _compute_image_1920(self):
        if self.shopify_variant_image_id:
            product_variant_image = self.env["product.image"].search(
                [("shopify_image_id", "=", self.shopify_variant_image_id)], limit=1)
            print("product_variant_image", product_variant_image)
            self.image_variant_1920 = product_variant_image.image_1920
        return super(productsDetails,self)._compute_image_1920()


    def update_product_variants(self, product, product_id):
        '''Update product variants'''
        product_variant = self.search([('product_tmpl_id', '=', product_id.id)])
        variants = product.get('variants')
        if variants:
            for variant in variants:
                # variant_image = self.env['product.image'].search([('shopify_image_id', '=', variant.get('image_id'))])
                # print("variant_image", variant_image)
                # print(type(variant_image.image_1920))
                # print("variant_image.image_1920",variant_image.image_1920)
                options = [variant.get(f'option{i}') for i in range(1, 4) if variant.get(f'option{i}')]
                for item in product_variant:
                    if item.product_template_attribute_value_ids:
                        list_values = [rec.name for rec in item.product_template_attribute_value_ids]
                        if set(options).issubset(set(list_values)):
                            item.is_shopify_variant = True
                            print("variant.get('image_id')",variant.get('image_id'))
                            item.shopify_variant_id = variant.get('id')
                            item.shopify_product_id = variant.get('product_id')
                            item.shopify_inventory_id = variant.get('inventory_item_id')
                            item.shopify_variant_image_id = variant.get('image_id') if variant.get('image_id') else product.get("image").get("id") if product.get("image") else False
                            item.barcode = variant.get('barcode')
                            item.weight = variant.get('weight')
                            item.lst_price = variant.get('price')
                            print("Variant Created")


