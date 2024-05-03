import base64
import requests
import json

from bs4 import BeautifulSoup

from odoo import fields, models, api
from odoo.exceptions import UserError


class productsDetails(models.Model):
    _inherit = 'product.template'
    _description = 'Product Details'

    shopify_product_id = fields.Char("Shopify ID")
    is_shopify_product = fields.Boolean("Shopify Product", default=False)
    is_exported_to_shopify = fields.Boolean("Exported to Shopify")

    # def write(self, vals):
    #     if not self.env.context.get('skip_export_flag'):
    #         vals.update({
    #             "is_exported_to_shopify": False,
    #         })
    #     res = super(productsDetails, self).write(vals)
    #     return res

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

    def update_tags(self, product, tag_list):
        '''Update product tags'''
        tags = product.get('tags')
        if tags:
            tags = tags.split(',')
            for tag in tags:
                tag_id = self.env['product.tag'].search([('name', '=', tag)], limit=1)
                if not tag_id:
                    tag_id = self.env['product.tag'].create({'name': tag})
                tag_list.append(tag_id.id)
        return tag_list

    def update_product_attributes(self, product, product_id):
        '''Update product attributes'''
        variable_list = []
        variants = product.get('options')
        if variants:
            for variant in variants:
                attribute_id = self.get_attribute(variant.get('name'))
                values = variant.get('values')
                value_list = self.get_attribute_values(attribute_id, values)

                if attribute_id and value_list:
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

    def update_product_variants(self, product, product_id):
        '''Update product variants'''
        product_variant = self.env['product.product'].search([('product_tmpl_id', '=', product_id.id)])
        variants = product.get('variants')
        if variants:
            for variant in variants:
                options = [variant.get(f'option{i}') for i in range(1, 4) if variant.get(f'option{i}')]
                for item in product_variant:
                    if item.product_template_attribute_value_ids:
                        list_values = [rec.name for rec in item.product_template_attribute_value_ids]
                        if set(options).issubset(set(list_values)):
                            item.shopify_variant_id = variant.get('id')
                            item.shopify_product_id = variant.get('product_id')
                            item.barcode = variant.get('barcode')
                            item.weight = variant.get('weight')
                            item.lst_price = variant.get('price')

    def update_product_images(self, product, product_id):
        '''Update product images'''
        images = product.get('images')
        if images:
            for image in images:
                image_data = None
                image_position = image.get('position')
                image_url = image.get('src')
                image_shopify = requests.get(image_url)
                image_data = base64.b64encode(image_shopify.content)

                if image_position == 1:
                    product_id.image_1920 = image_data
                else:
                    image_id = self.env['product.image'].search([('shopify_image_id', '=', str(image.get('id')))])
                    if not image_id:
                        image_id = self.env['product.image'].create({
                            'shopify_image_id': image.get('id'),
                            'product_tmpl_id': product_id.id,
                            'name': product["title"],
                            'sequence': image_position,
                            'image_1920': image_data,
                        })
        else:
            product_id.image_1920 = False

    @api.model
    def update_products(self, response_data):
        '''Update products based on Shopify response data'''
        productenv = self.env['product.template']
        products = response_data.get("products", [response_data])

        for product_data in products:
            tag_list = []
            tag_list = self.update_tags(product_data, tag_list)

            product_description = False
            if product_data.get('body_html'):
                soup = BeautifulSoup(product_data.get('body_html'), 'html.parser')
                product_description = soup.get_text()

            product_values = {
                'shopify_product_id': str(product_data["id"]),
                'name': product_data["title"],
                'description': product_description,
                'detailed_type': 'product',
                'product_tag_ids': [(6, 0, tag_list)],
            }

            product_id = productenv.search([('shopify_product_id', '=', str(product_data["id"]))])
            if not product_id:
                product_id = self.env['product.template'].create(product_values)
            else:
                product_id.write(product_values)

            self.update_product_attributes(product_data, product_id)
            self.update_product_variants(product_data, product_id)
            self.update_product_images(product_data, product_id)

    def export_products(self):

        without_shopify_id_products = self.env['product.template'].search([("shopify_product_id", "=", False),
                                                                           ("is_exported_to_shopify", "=", False),
                                                                           ("is_shopify_product", "=", True), ])
        # If the customer do not have Shopify ID so that customer is not present on Shopify
        # therefore during export we have to create the customer

        with_shopify_id_products = self.env['product.template'].search([("shopify_product_id", "!=", False),
                                                                        ("is_exported_to_shopify", "=", False),
                                                                        ("is_shopify_product", "=", True)])
        # If the customer have Shopify ID so that customer is  present on Shopify
        # therefore during export we have to update the customer

        print("without_shopify_id_products", without_shopify_id_products)
        print("with_shopify_id_products", with_shopify_id_products)

        store = self.env['ir.config_parameter']
        baseURL = store.search([('key', '=', 'hspl_shopify.baseStoreURL')]).value
        access_token = store.search([('key', '=', 'hspl_shopify.access_token')]).value

        if baseURL and access_token:
            headers = {
                'X-Shopify-Access-Token': access_token,
                "Content-Type": "application/json"
            }

            if without_shopify_id_products:
                # make POST request
                for product in without_shopify_id_products:

                    values = self.get_export_product_values(product)

                    url = f"{baseURL}/products.json"
                    print("(values)", (values))
                    # print("json.dumps(values)", json.dumps(values))
                    response = requests.request(method="POST", url=url, headers=headers, data=json.dumps(values))
                    error = response.json().get("errors")
                    print("response.status_code", response.status_code)
                    print("error", error)

                    if response.status_code == 201:
                        response_data = response.json()
                        print("response_data", response_data)
                        response_product = response_data.get("product")
                        product.with_context(skip_export_flag=True).write({
                            "shopify_product_id": response_product.get("id"),
                            "is_exported_to_shopify": True,
                        })
                        product_variant = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
                        variants = response_product.get('variants')
                        if variants:
                            for variant in variants:
                                options = [variant.get(f'option{i}') for i in range(1, 4) if variant.get(f'option{i}')]
                                for item in product_variant:
                                    if item.product_template_attribute_value_ids:
                                        list_values = [rec.name for rec in item.product_template_attribute_value_ids]
                                        if set(options).issubset(set(list_values)):
                                            item.shopify_variant_id = variant.get('id')
                                            item.shopify_product_id = variant.get('product_id')

                        print("Product Exported")

                    else:
                        raise UserError(
                            f"Failed to export data for product id ={product.id}. Response {response.status_code}- {error}")

            if with_shopify_id_products:

                for product in with_shopify_id_products:
                    values = self.get_export_product_values(product)
                    url = f"{baseURL}/products/{product.shopify_product_id}.json"
                    response = requests.request("PUT", url, headers=headers, data=json.dumps(values))
                    error = response.json().get("errors")

                    if response.status_code == 200:
                        product.with_context(skip_export_flag=True).write({
                            "is_exported_to_shopify": True,
                        })

                    else:
                        raise UserError(
                            f"Failed to export data for product id ={product.id}. Response {response.status_code}.{error}")
        else:
            raise UserError("Improper Store Details")

    def get_export_product_values(self, product):

        tag_vals = ','.join(str(tag.name) for tag in product.product_tag_ids) if product.product_tag_ids else ''
        if not product.attribute_line_ids:
            data = {
                "product": {
                    "title": product.name,
                    'tags': tag_vals,
                    "variants": [
                        {
                            "title": "Default Title",
                            "price": product.list_price,
                            "sku": "",
                            "position": 1,
                            "option1": "Default Title",
                            "option2": "",
                            "option3": "",
                            "barcode": product.barcode,
                        }
                    ],
                    "options": [
                        {
                            "name": "Title",
                            "position": 1,
                            "values": [
                                "Default Title"
                            ]
                        }
                    ],
                }
            }
        else:
            data = {
                "product": {
                    "title": product.name,
                    'tags': tag_vals,
                }
            }

            option_list = []
            if product.attribute_line_ids:
                for attr in product.attribute_line_ids:
                    val_list = []
                    for val in attr.value_ids:
                        val_list.append(val.name)
                    attr_vals = {
                        "name": attr.attribute_id.name,
                        "values": val_list
                    }
                    option_list.append(attr_vals)

            product_variant_ids = self.env['product.product'].search(
                [('product_tmpl_id', '=', product.id)])
            variant_val_list = []
            if product_variant_ids:
                for variant in product_variant_ids:
                    variant_val = {}
                    if variant.product_template_variant_value_ids:
                        count = 1
                        for value in variant.product_template_variant_value_ids:
                            if count == 1:
                                variant_val['option1'] = value.name
                            elif count == 2:
                                variant_val['option2'] = value.name
                            else:
                                variant_val['option3'] = value.name
                            count += 1
                        variant_val['price'] = variant.lst_price
                        variant_val_list.append(variant_val)

            data.get('product')['variants'] = variant_val_list
            data.get('product')['options'] = option_list

            image_list = []
            product_images = self.env['product.image'].search([("product_tmpl_id", "=", product.id)])

            if product_images:
                position = 1
                for product_image in product_images:
                    image_dic = {
                        'position': position,
                        'name': product_image.name,
                        # 'attachment': product.image_1920 if position == 1 else product_image.image_1920,
                    }
                    image_list.append(image_dic)
                    position += 1

                data.get('product')['images'] = image_list
        return data
