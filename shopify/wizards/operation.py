import requests

from odoo import models, fields, api
from odoo.exceptions import UserError


class operationImport(models.TransientModel):
    _name = 'shopify.operation'
    _description = 'Importing the data'

    operation_for = fields.Selection([
        ('customers', 'Customer'),
        ('products', 'Product'),
        ('orders', 'Orders'),
    ], string="Operation", default="customers")

    def action_import_data(self):

        try:
            store = self.env['ir.config_parameter']

            baseURL = store.search([('key', '=', 'shopify.baseStoreURL')]).value
            access_token = store.search([('key', '=', 'shopify.access_token')]).value

            print(baseURL)
            print(access_token)

            if baseURL and access_token:
                url = f"{baseURL}/{self.operation_for}.json"

                payload = {}
                headers = {
                    'X-Shopify-Access-Token': access_token,
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                if response.status_code == 200:
                    response_data = response.json()
                else:
                    print(f"Error: {response.status_code}")
                    raise UserError(f"Error: {response.status_code}")

                operatefunc = f"update_{self.operation_for}"
                getattr(self, operatefunc)(response_data)

                # if self.operation_for == 'customers':
                #     operateClass = self.env['res.partner']
                # elif self.operation_for == 'products':
                #     operateClass = self.env['product.product']
                # elif self.operation_for == 'orders':
                #     operateClass = self.env['sale.order']
                #
                # getattr(operateClass,operatefunc)(response_data)

            else:
                raise UserError("Improper Store Details")

        except Exception as e:
            raise e

    def update_customers(self, response_data):
        for rec in self:
            partners = self.env['res.partner']
            list_customers = response_data.get("customers")
            for customer in list_customers:
                values = {
                    'shopify_customer_id': str(customer.get("id")),
                    'email': customer.get("email"),
                    'name': customer.get("first_name") + ' ' + customer.get("last_name"),
                    'mobile': customer.get("phone"),
                    'street': customer.get("addresses")[0].get('address1'),
                    'street2': customer.get("addresses")[0].get('address2'),
                    'city': customer.get("addresses")[0].get('city'),
                    'zip': customer.get("addresses")[0].get('zip'),
                }
                # Determine state and country based on received data
                state_name = customer.get("addresses")[0].get('province')
                country_name = customer.get("addresses")[0].get('country')

                state_id = False
                country_id = False

                if state_name:
                    state = rec.env['res.country.state'].search([('name', '=ilike', state_name)], limit=1)
                    if state:
                        state_id = state.id

                if country_name:
                    country = rec.env['res.country'].search([('name', '=ilike', country_name)], limit=1)
                    if country:
                        country_id = country.id

                values.update({
                    'state_id': state_id,
                    'country_id': country_id,
                })
                print(values)

                partner_exist = partners.search([('shopify_customer_id', '=', values['shopify_customer_id'])])
                try:
                    if partner_exist:
                        partner_exist.write(values)
                        print("Partner Updated")
                    else:
                        partners.create(values)
                        print("Partner Created")
                except Exception as e:
                    raise e

    def update_products(self, response_data):
        for rec in self:
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

                varaible_list = []
                attribute_line = {}
                # attribute_list = []
                value_list = []
                variants = product.get('options')

                if variants:
                    for variant in variants:
                        attribute_id = self.env['product.attribute'].search([('name', '=', variant.get('name'))],
                                                                            limit=1)
                        if not attribute_id:
                            attribute_id = self.env['product.attribute'].create({
                                'name': variant.get('name'),
                                'display_type': 'radio',
                                'create_variant': 'always',
                                'visibility': 'visible',
                            })
                        print('attribute_id',attribute_id)


                        values = variant.get('values')
                        for value in values:
                            value_id = self.env['product.attribute.value']
                            if not value_id:
                                value_id = self.env['product.attribute.value'].create({
                                    'name': value,
                                    'attribute_id': attribute_id.id,
                                })
                                value_list.append(value_id.id)
                            else:
                                value_list.append(value_id.id)

                        attribute_line.update({
                            'attribute_id': attribute_id.id,
                            'value_ids': [(6, 0, value_list)]
                        })
                        varaible_list.append(attribute_line)

                for pro in products:
                    values = {
                        'shopify_product_id': str(pro["id"]),
                        'name': pro["title"],
                        'product_tag_ids': [(6, 0, tag_list)],
                        'attribute_line_ids': [(6, 0, varaible_list)]
                    }
                    print("Valueeeeeees", values)

                    product_exist = productenv.search([('shopify_product_id', '=', str(product["id"]))])
                    print("product_exist", product_exist)
                    try:
                        if product_exist:
                            productenv.write(values)
                            print("Product Updated")
                        else:
                            productenv.create(values)
                            print("Product   Created")
                    except Exception as e:
                        raise e

        print("Product printed")

    def update_orders(self, response_data):

        # for rec in self:
        #     saleorder = self.env['sale.order']
        #     list_orders = response_data.get("orders")
        #
        #     for order in list_orders:
        #         values = {
        #             'shopify_orders_id': str(order.get("id")),
        #         }

        print("Orders printed")
