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

                product_values = {
                    'shopify_product_id': str(product["id"]),
                    'name': product["title"],
                    'detailed_type': 'product',
                    'product_tag_ids': [(6, 0, tag_list)],
                }

                print('product_values.....', product_values)

                product_id = productenv.search([('shopify_product_id', '=', str(product["id"]))])
                if not product_id:
                    product_id = self.env['product.template'].create(product_values)
                    print('Template Created')
                else:
                    product_id.write(product_values)
                    print('Template Updated')

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
                                print('attribute_line===', attribute_line)

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
                        print('options//////', options)

                        for item in product_variant:
                            if item.product_template_attribute_value_ids:
                                print('-----item', item)
                                print('item.product_template_attribute_value_ids',
                                      item.product_template_attribute_value_ids)
                                list_values = []
                                for rec in item.product_template_attribute_value_ids:
                                    list_values.append(rec.name)
                                print('list_values---->', list_values)

                                if set(options).issubset(set(list_values)):
                                    item.shopify_variant_id = variant.get('id')
                                    item.shopify_product_id = variant.get('product_id')
                                    item.barcode = variant.get('barcode')
                                    item.weight = variant.get('weight')
                                    item.lst_price = variant.get('price')

    def update_orders(self, response_data):

        for rec in self:
            orderenv = self.env['sale.order']

            orders = response_data.get('orders')
            for order in orders:

                customer_shopify_id = str(order.get('customer').get('id'))
                customer_id = self.env['res.partner'].search([('shopify_customer_id', '=', str(customer_shopify_id))])

                billing_name = order.get('billing_address').get('name')
                billing_id = self.env['res.partner'].search([('name', '=', billing_name)], limit=1)

                shipping_name = order.get('shipping_address').get('name')
                shipping_id = self.env['res.partner'].search([('name', '=', shipping_name)], limit=1)

                values = {
                    'shopify_orders_id': order.get('id'),
                    'partner_id': customer_id.id,
                    'partner_invoice_id': billing_id.id,
                    'partner_shipping_id': shipping_id.id,
                }

                order_id = orderenv.search([('shopify_orders_id', '=', str(order.get('id')))])
                if not order_id:
                    order_id = orderenv.create(values)
                else:
                    order_id.write(values)

                line_items = order.get('line_items')
                for line_item in line_items:
                    variant_id = line_item.get('variant_id')

                    product_variant = self.env['product.product'].search([('shopify_variant_id', '=', str(variant_id) )])
                    product_variant_id = product_variant.id
                    product = product_variant.shopify_product_id

                    for tax in line_item.get('tax_lines'):
                        tax_title = tax.get('title')
                        tax_rate = (tax.get('rate')) * 100

                    order_line_values = {
                        'order_id': order_id.id,
                        'product_id': product_variant_id,
                        'product_uom_qty': line_item.get('quantity'),
                        'discount': float(line_item.get('total_discount')) * 100,
                    }

                    order_line = self.env['sale.order.line'].search([
                        ('order_id', '=', order_id.id),
                        ('product_id', '=', product_variant_id),
                        ('product_uom_qty', '=', line_item.get('quantity')),
                        ('discount', '=', float(line_item.get('total_discount')) * 100),
                    ])
                    if not order_line:
                        order_line = self.env['sale.order.line'].create(order_line_values)
                    else:
                        order_line.write(order_line_values)

        print("Orders printed")
