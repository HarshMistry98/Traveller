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

    shopify_product_image_id = fields.Char("Shopify Product Image ID")

    shopify_product_status = fields.Selection([
        ('active', 'Active'),
        ('draft', 'Draft'),
    ], default='draft', required=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(productsDetails, self).create(vals_list)
        for record in records:
            for val in vals_list:
                if val.get("image_1920"):
                    image_values = {
                        "name": val.get("name"),
                        "sequence": 1,
                        "product_tmpl_id": record.id,
                        "image_1920": val.get("image_1920"),
                    }
                    tmpl_image = self.env['product.image'].search([('sequence', "=", 1),
                                                                   ("product_tmpl_id", "=", self.id),
                                                                   ("image_1920", "=", val.get("image_1920"))])
                    if not tmpl_image:
                        self.env['product.image'].create(image_values)
        return records

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
            attribute_id = self.env['product.attribute'].with_user(
                self.env.ref("hspl_shopify.shopify_user_root")).create({
                'name': attribute_name,
                'display_type': 'radio',
                'create_variant': 'always',
                'visibility': 'visible',
            })
        return attribute_id

    def get_attribute_values(self, attribute_id, values):
        '''Function to return the values of corresponding attibute id if exist or creates the new value for provided attribute'''
        value_ids = []
        for value in values:
            value_id = self.env['product.attribute.value'].search(
                [('name', '=', value), ('attribute_id', '=', attribute_id)], limit=1)
            if not value_id:
                value_id = self.env['product.attribute.value'].with_user(
                    self.env.ref("hspl_shopify.shopify_user_root")).create({
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
                    tag_id = self.env['product.tag'].with_user(self.env.ref("hspl_shopify.shopify_user_root")).create(
                        {'name': tag})
                tag_list.append(tag_id.id)
        return tag_list

    def update_product_attributes(self, product, product_id):
        '''Update product attributes'''
        variable_list = []
        variants = product.get('options')
        if variants:
            for variant in variants:
                attribute = self.get_attribute(variant.get('name'))
                if attribute.name != "Title":
                    values = variant.get('values')
                    value_list = self.get_attribute_values(attribute.id, values)

                    if attribute.id and value_list:
                        attribute_line = self.env['product.template.attribute.line'].search(
                            [('attribute_id', '=', attribute.id),
                             ('value_ids', 'in', value_list),
                             ('product_tmpl_id', '=', product_id.id)], limit=1)
                        if not attribute_line:
                            attribute_line = self.env['product.template.attribute.line'].with_user(
                                self.env.ref("hspl_shopify.shopify_user_root")).create({
                                'attribute_id': attribute.id,
                                'value_ids': [(6, 0, value_list)],
                                'product_tmpl_id': product_id.id
                            })
                        else:
                            attribute_line.with_user(self.env.ref("hspl_shopify.shopify_user_root")).write({
                                'attribute_id': attribute.id,
                                'value_ids': [(6, 0, value_list)],
                                'product_tmpl_id': product_id.id
                            })

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
                    product_id.shopify_product_image_id = image.get("id", "")
                image_id = self.env['product.image'].search([('shopify_image_id', '=', str(image.get('id')))])
                image_values = {
                    'shopify_image_id': image.get('id'),
                    'product_tmpl_id': product_id.id,
                    'name': product["title"],
                    'sequence': image.get('position'),
                    'image_1920': image_data,
                }
                if not image_id:
                    self.env['product.image'].with_user(self.env.ref("hspl_shopify.shopify_user_root")).create(
                        image_values)
                else:
                    image_id.with_user(self.env.ref("hspl_shopify.shopify_user_root")).write(image_values)

    def s_update_product_images(self, product, product_id):
        images = product.get('images')
        if images:
            for image in images:
                template_image = True
                variant_image = True
                image_data = None
                image_position = image.get('position')
                image_url = image.get('src')
                image_shopify = requests.get(image_url)
                image_data = base64.b64encode(image_shopify.content)

                if image_position == 1:
                    product_id.image_1920 = image_data
                    product_id.shopify_product_image_id = image.get("id", "")

                variant_ids = image.get("variant_ids")
                variant_list = []
                if variant_ids:
                    for variant_id in variant_ids:
                        product_variant = self.env['product.product'].search(
                            [("shopify_variant_id", "=", str(variant_id))])
                        product_variant.image_variant_1920 = image_data
                        variant_list.append(product_variant.id)

                image_id = self.env['shopify.image'].search([('shopify_image_id', '=', str(image.get('id')))])
                image_values = {
                    'shopify_image_id': image.get('id'),
                    'shopify_product_id': image.get('product_id'),
                    'product_tmpl_id': product_id.id,
                    'product_variant_ids': [(6, 0, variant_list)],
                    'name': product["title"],
                    'position': image.get('position'),
                    'image_1920': image_data,
                }
                if not image_id:
                    self.env['shopify.image'].with_user(self.env.ref("hspl_shopify.shopify_user_root")).create(
                        image_values)
                else:
                    image_id.with_user(self.env.ref("hspl_shopify.shopify_user_root")).write(image_values)

    @api.model
    def update_products(self, response_data=False):
        '''Update products based on Shopify response data'''
        productenv = self.env['product.template']

        if not response_data:
            store = self.env['ir.config_parameter']

            baseURL = store.get_param('hspl_shopify.baseStoreURL')
            access_token = store.get_param('hspl_shopify.access_token')
            if baseURL and access_token:
                url = f"{baseURL}/products.json"

                payload = {}
                headers = {
                    'X-Shopify-Access-Token': access_token,
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                if response.status_code == 200:
                    response_products_data = response.json()
                    products = response_products_data.get('products')
                else:
                    raise UserError(f"Error: {response.status_code}")
            else:
                raise UserError("Improper Store Details")

        else:
            products = [response_data]

        for product_data in products:
            tag_list = []
            tag_list = self.update_tags(product_data, tag_list)

            product_description = False
            if product_data.get('body_html'):
                soup = BeautifulSoup(product_data.get('body_html'), 'html.parser')
                product_description = soup.get_text()

            product_values = {
                'shopify_product_id': product_data["id"],
                'is_shopify_product': True,
                'is_exported_to_shopify': True,
                'name': product_data["title"],
                'description': product_description,
                'shopify_product_status': product_data.get("status"),
                'detailed_type': 'product',
                'product_tag_ids': [(6, 0, tag_list)],
            }

            product_id = productenv.search([('shopify_product_id', '=', str(product_data["id"]))])
            if not product_id:
                product_id = self.env['product.template'].with_user(
                    self.env.ref("hspl_shopify.shopify_user_root")).create(product_values)
            else:
                product_id.with_context(skip_export_flag=True).with_user(
                    self.env.ref("hspl_shopify.shopify_user_root")).write(product_values)

            self.update_product_attributes(product_data, product_id)
            self.update_product_images(product_data, product_id)
            self.env['product.product'].update_product_variants(product_data, product_id)

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

        store = self.env['ir.config_parameter']
        baseURL = store.get_param('hspl_shopify.baseStoreURL')
        access_token = store.get_param('hspl_shopify.access_token')

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
                    response = requests.request(method="POST", url=url, headers=headers, data=json.dumps(values))
                    error = response.json().get("errors")

                    if response.status_code == 201:
                        response_data = response.json()
                        response_product = response_data.get("product")
                        product_template_shopify_image_id = False
                        response_product_images = response_product.get("images")
                        if response_product_images:
                            for image in response_product_images:
                                if image.get("position") == 1:
                                    product_template_shopify_image_id = image.get("id")
                        value_to_update = {
                            "shopify_product_id": response_product.get("id"),
                            "is_exported_to_shopify": True,
                            'shopify_product_image_id': product_template_shopify_image_id,
                        }
                        product.with_context(skip_export_flag=True).with_user(
                            self.env.ref("hspl_shopify.shopify_user_root")).write(value_to_update)
                        product_variant = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
                        variants = response_product.get('variants')
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
                                            item.shopify_variant_image_id = variant.get("image_id")
                                            variant_image = self.env['product.image'].search([
                                                ("product_tmpl_id", "=", product.id),
                                                ("product_variant_id", "=", item.id),
                                            ])
                                            image_values = {
                                                'name': item.name,
                                                'shopify_image_id': variant.get("image_id"),
                                                'image_1920': item.image_1920,
                                            }
                                            if not variant_image:
                                                self.env['product.image'].create(image_values)
                                            else:
                                                variant_image.write(image_values)

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
                        product.with_context(skip_export_flag=True).with_user(
                            self.env.ref("hspl_shopify.shopify_user_root")).write({
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
                    "status": product.shopify_product_status,
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
                            'attachment': product.image_1920.decode("utf-8"),
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
                    "status": product.shopify_product_status,
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
            for product_image in product_images:
                image_dic = {
                    'position': product_image.sequence,
                    'name': product_image.name,
                    'attachment': product_image.image_1920.decode("utf-8"),
                    'product_id': product_image.product_tmpl_id.shopify_product_id,
                }
                variant_list = []
                if product_image.product_variant_id:
                    variant_list.append(product_image.product_variant_id.shopify_variant_id)
                image_dic['variant_ids']: variant_list
                image_list.append(image_dic)

            data.get('product')['images'] = image_list
        return data

    def activate_shopify_product(self):
        for product_id in self._context.get("active_ids"):
            product = self.env['product.template'].browse(product_id)
            store = self.env['ir.config_parameter']
            baseURL = store.get_param('hspl_shopify.baseStoreURL')
            access_token = store.get_param('hspl_shopify.access_token')
            if baseURL and access_token:
                url = f"{baseURL}/products/{product.shopify_product_id}.json"
                headers = {
                    'X-Shopify-Access-Token': access_token,
                    "Content-Type": "application/json"
                }
                product_values = {
                    "product": {
                        "id": int(product.shopify_product_id),
                        "status": "active",
                    }
                }
                response = requests.request("PUT", url, headers=headers, data=json.dumps(product_values))

                if response.status_code == 200:
                    product_response = response.json().get('product')

                    product.with_user(self.env.ref("hspl_shopify.shopify_user_root")).write({
                        "shopify_product_status": product_response.get("status"),
                    })
                else:
                    raise UserError(f"Error: {response.status_code} {response.text}")
            else:
                raise UserError("Improper Store Details")

    def draft_shopify_product(self):
        for product_id in self._context.get("active_ids"):
            product = self.env['product.template'].browse(product_id)
            store = self.env['ir.config_parameter']
            baseURL = store.get_param('hspl_shopify.baseStoreURL')
            access_token = store.get_param('hspl_shopify.access_token')
            if baseURL and access_token:
                url = f"{baseURL}/products/{product.shopify_product_id}.json"
                headers = {
                    'X-Shopify-Access-Token': access_token,
                    "Content-Type": "application/json"
                }
                product_values = {
                    "product": {
                        "id": int(product.shopify_product_id),
                        "status": "draft"
                    }
                }
                response = requests.request("PUT", url=url, headers=headers, data=json.dumps(product_values))

                if response.status_code == 200:
                    product_response = response.json().get('product')

                    product.with_user(self.env.ref("hspl_shopify.shopify_user_root")).write({
                        "shopify_product_status": product_response.get("status"),
                    })
                else:
                    raise UserError(f"Error: {response.status_code} {response.text}")
            else:
                raise UserError("Improper Store Details")
