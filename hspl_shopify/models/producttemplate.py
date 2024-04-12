import base64

from odoo import fields, models, api
import requests


class productsDetails(models.Model):
    _inherit = 'product.template'
    _description = 'Product Details'

    shopify_product_id = fields.Char("Shopify ID")

    def get_attribute(self, attribute_name):
        '''Function to return the attribute id if exist or creates the new attribute'''

        attribute_id = self.env['product.attribute'].search([('name', '=', attribute_name)], limit=1)
        if not attribute_id:
            attribute_id = self.env['product.attribute'].create({
                'name': attribute_name,
                'display_type': 'radio',
                'create_variant': 'always',
                'visibility': 'visible',
            })
        return attribute_id.id

    def get_attribute_values(self, attribute_id, values):
        '''Function to return the values of corresponding attibute id if exist or creates the new value for provided attribute'''

        value_ids = []
        for value in values:
            value_id = self.env['product.attribute.value'].search(
                [('name', '=', value), ('attribute_id', '=', attribute_id)], limit=1)
            if not value_id:
                value_id = self.env['product.attribute.value'].create({
                    'name': value,
                    'attribute_id': attribute_id,
                })
            value_ids.append(value_id.id)
        return value_ids

    def update_products(self, response_data):
        productenv = self.env['product.template']

        products = response_data["products"]

        for product in products:

            tags = product.get('tags')
            tag_list = []
            if tags:
                tags = tags.split(',')
                for tag in tags:
                    tag_id = self.env['product.tag'].search([('name', '=', tag)], limit=1)
                    if not tag_id:
                        tag_id = self.env['product.tag'].create({'name': tag})
                        tag_list.append(tag_id.id)
                    else:
                        tag_list.append(tag_id.id)

            product_values = {
                'shopify_product_id': str(product["id"]),
                'name': product["title"],
                'detailed_type': 'product',
                'product_tag_ids': [(6, 0, tag_list)],
            }

            product_id = productenv.search([('shopify_product_id', '=', str(product["id"]))])
            if not product_id:
                product_id = self.env['product.template'].create(product_values)
            else:
                product_id.write(product_values)

            variable_list = []
            variants = product.get('options')

            if variants:
                for variant in variants:
                    attribute_id = self.get_attribute(variant.get('name'))

                    values = variant.get('values')
                    value_list = self.get_attribute_values(attribute_id, values)

                    if attribute_id:
                        if value_list:
                            attribute_line = self.env['product.template.attribute.line'].search(
                                [('attribute_id', '=', attribute_id),
                                 ('value_ids', 'in', value_list),
                                 ('product_tmpl_id', '=', product_id.id)], limit=1)
                            if not attribute_line:
                                attribute_line = self.env['product.template.attribute.line'].create({
                                    'attribute_id': attribute_id,
                                    'value_ids': [(6, 0, value_list)],
                                    'product_tmpl_id': product_id.id
                                })
                            else:
                                attribute_line.write({
                                    'attribute_id': attribute_id,
                                    'value_ids': [(6, 0, value_list)],
                                    'product_tmpl_id': product_id.id
                                })

            product_variant = self.env['product.product'].search(
                [('product_tmpl_id', '=', product_id.id)])

            variants = product.get('variants')
            if variants:
                for variant in variants:
                    options = []
                    if variant.get('option1') == 'Default Title' and product_id:
                        product_id.sudo().write({
                            'list_price': variant.get('price'),
                            'weight': variant.get('weight'),
                        })

                    if variant.get('option1'):
                        options.append(variant.get('option1'))
                    if variant.get('option2'):
                        options.append(variant.get('option2'))
                    if variant.get('option3'):
                        options.append(variant.get('option3'))

                    for item in product_variant:
                        if item.product_template_attribute_value_ids:
                            list_values = []
                            for rec in item.product_template_attribute_value_ids:
                                list_values.append(rec.name)

                            if set(options).issubset(set(list_values)):
                                item.shopify_variant_id = variant.get('id')
                                item.shopify_product_id = variant.get('product_id')
                                item.barcode = variant.get('barcode')
                                item.weight = variant.get('weight')
                                item.lst_price = variant.get('price')

            image_ids = []
            images = product.get('images')
            if images:
                for image in images:
                    image_position = image.get('position')
                    print('image_position', image_position)

                    image_url = image.get('src')

                    image_shopify = requests.get(image_url)
                    image_data = base64.b64encode(image_shopify.content)

                    if image_position == 1:
                        first_image = image_data
                        product_id.image_1920 = first_image
                        print('product_id', product_id.id)
                        print('first image')
                    else:
                        image_id = self.env['product.image'].search([('product_tmpl_id', '=', product_id.id),
                                                                     ('name', '=', product["title"]),
                                                                     ('image_1920', '=', image_data)])
                        print('Present image_id.id', image_id.id)

                        if not image_id:
                            image_id = self.env['product.image'].create({
                                'product_tmpl_id': product_id.id,
                                'name': product["title"],
                                'image_1920': image_data,
                            })
                            print('Created image_id.id', image_id.id)

                        image_ids.append(image_id.id)
                        print(image_ids)
                        product_id.product_template_image_ids = [(6, 0, image_ids)]
            else:
                product_id.image_1920 = False

