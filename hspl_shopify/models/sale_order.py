from odoo import fields, models
import requests
import json

from odoo.exceptions import UserError


class SaleOrderLineDetails(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Order Line'

    shopify_order_line_id = fields.Char("Shopify ID")


class ordersDetails(models.Model):
    _inherit = 'sale.order'
    _description = 'Order Details'

    shopify_orders_id = fields.Char("Shopify ID")
    is_shopify_order = fields.Boolean("Shopify Order", default=False)
    is_exported_to_shopify = fields.Boolean("Exported to Shopify")

    def write(self, vals):
        if not self.env.context.get('skip_export_flag'):
            vals.update({
                "is_exported_to_shopify": False,
            })
        res = super(ordersDetails, self).write(vals)
        return res

    def get_order_values(self, order, default_location_id):

        customer_shopify_id = str(order.get('customer').get('id'))
        customer_id = self.env['res.partner'].search([('shopify_customer_id', '=', str(customer_shopify_id))])

        billing_name = order.get('billing_address').get('name')
        billing_id = self.env['res.partner'].search([('name', '=', billing_name)], limit=1)

        shipping_name = order.get('shipping_address').get('name')
        shipping_id = self.env['res.partner'].search([('name', '=', shipping_name)], limit=1)

        fulfillment_status = order.get('fulfillment_status')
        if fulfillment_status in ['fulfilled']:
            payment_status = 'sale'
        else:
            payment_status = 'draft'

        values = {
            'shopify_orders_id': order.get('id'),
            'is_exported_to_shopify': True,
            'is_shopify_order': True,
            'partner_id': customer_id.id,
            'partner_invoice_id': billing_id.id,
            'partner_shipping_id': shipping_id.id,
            'state': payment_status,
            # 'warehouse_id': warehouse_name.id if warehouse_name else None
        }
        warehouse_name = self.env['stock.warehouse'].search([("shopify_warehouse_id", "=", default_location_id)],
                                                            limit=1)

        if warehouse_name:
            values["warehouse_id"] = warehouse_name.id
        return values

    def get_taxes(self, line_item):
        tax_ids = []
        for tax in line_item.get('tax_lines'):
            tax_rate = (tax.get('rate')) * 100
            tax_title = tax.get('title')
            tax_group_id = self.env['account.tax.group'].search([('name', '=', tax_title)], limit=1).id
            tax_id = self.env['account.tax'].search([('type_tax_use', '=', 'sale'),
                                                     ('amount', '=', tax_rate),
                                                     ('tax_group_id', '=', tax_group_id)]).id
            tax_ids.append(tax_id)
        return tax_ids

    def create_order_lines(self, order, order_id):
        line_items = order.get('line_items')
        order_line_list = []
        for line_item in line_items:
            variant_id = line_item.get('variant_id')
            product_variant = self.env['product.product'].search([('shopify_variant_id', '=', str(variant_id))])
            if not product_variant:
                store = self.env['ir.config_parameter']
                baseURL = store.search([('key', '=', 'hspl_shopify.baseStoreURL')]).value
                access_token = store.search([('key', '=', 'hspl_shopify.access_token')]).value

                if baseURL and access_token:
                    # url = f"{baseURL}/customers.json"

                    payload = {}
                    headers = {
                        'X-Shopify-Access-Token': access_token,
                    }
                else:
                    raise UserError("Improper Store Details")
                url = f"{baseURL}/products/{line_item.get('product_id')}.json"
                response = requests.request("GET", url=url, headers=headers, data=payload)
                if response.status_code == 200:
                    response_product_data = response.json()
                    product_data = response_product_data.get('product')
                    self.env['product.template'].update_products(response_data=product_data)
                    print("Product created")
                    product_variant = self.env['product.product'].search([('shopify_variant_id', '=', str(variant_id))])
                else:
                    print(f"Error: {response.status_code}")
                    raise UserError(f"Error: {response.status_code}")

            tax_ids = self.get_taxes(line_item)
            order_line_values = {
                'name': line_item.get("name"),
                'shopify_order_line_id': line_item.get("id"),
                'order_id': order_id.id,
                'product_id': product_variant.id,
                'product_uom_qty': line_item.get('quantity'),
                'tax_id': [(6, 0, tax_ids)],
                'discount': float(line_item.get('total_discount')) * 100,
                'customer_lead': 5.0,
            }
            print("order_line_values",order_line_values)
            order_line = self.env['sale.order.line'].search([
                ('shopify_order_line_id', '=', line_item.get("id")),
            ])
            if not order_line:
                order_line = self.env['sale.order.line'].create(order_line_values)
            else:
                order_line.write(order_line_values)
            order_line_list.append(order_line.id)

        # return order_line_list

    def update_orders(self, response_data=False):
        orderenv = self.env['sale.order']

        store = self.env['ir.config_parameter']

        baseURL = store.search([('key', '=', 'hspl_shopify.baseStoreURL')]).value
        access_token = store.search([('key', '=', 'hspl_shopify.access_token')]).value

        headers = {
            'X-Shopify-Access-Token': access_token,
        }
        if baseURL and access_token:
            payload = {}
            shop_url = f"{baseURL}/shop.json"
            shop_response = requests.request("GET", shop_url, headers=headers, data=payload).json()
            default_location_id = ""
            if shop_response:
                shop_data = shop_response.get("shop", "")
                if shop_data:
                    default_location_id = shop_data.get("primary_location_id")

            if not response_data:
                url = f"{baseURL}/orders.json"
                response = requests.request("GET", url=url, headers=headers, data=payload)

                if response.status_code == 200:
                    response_orders_data = response.json()
                    orders = response_orders_data.get('orders')
                else:
                    print(f"Error: {response.status_code}")
                    raise UserError(f"Error: {response.status_code}")
            else:
                orders = [response_data]
        else:
            raise UserError("Improper Store Details")

        for order in orders:
            customer = order.get("customer", "")
            customer_exist = self.env['res.partner'].search([("shopify_customer_id", "=", customer.get("id"))])
            if not customer_exist:
                url = f"{baseURL}/customers/{customer.get('id')}.json"
                response = requests.request("GET", url=url, headers=headers, data=payload)
                if response.status_code == 200:
                    response_customer_data = response.json()
                    customer_data = response_customer_data.get('customer')
                    self.env['res.partner'].update_customers(response_data=customer_data)
                    print("Customer created")
                else:
                    print(f"Error: {response.status_code}")
                    raise UserError(f"Error: {response.status_code}")

            values = self.get_order_values(order, default_location_id)
            order_id = orderenv.search([('shopify_orders_id', '=', str(order.get('id')))])
            if not order_id:
                order_id = orderenv.with_user(self.env.ref("hspl_shopify.shopify_user_root")).create(values)
            else:
                order_id.with_user(self.env.ref("hspl_shopify.shopify_user_root")).write(values)
            # Creating Order Lines
            self.create_order_lines(order, order_id)

    def export_orders(self):
        print("Exporting Orders")

        without_shopify_id_orders = self.env['sale.order'].search([("shopify_orders_id", "=", False),
                                                                   ("is_exported_to_shopify", "=", False),
                                                                   ("is_shopify_order", "=", True), ])
        # If the order do not have Shopify ID so that order is not present on Shopify
        # therefore during export we have to create the order by POST request

        with_shopify_id_orders = self.env['sale.order'].search([("shopify_orders_id", "!=", False),
                                                                ("is_exported_to_shopify", "=", False),
                                                                ("is_shopify_order", "=", True)])
        # If the order have Shopify ID so that order is  present on Shopify
        # therefore during export we have to update the order by PUT request

        print("without_shopify_id_orders", without_shopify_id_orders)
        print("with_shopify_id_orders", with_shopify_id_orders)

        store = self.env['ir.config_parameter']
        baseURL = store.search([('key', '=', 'hspl_shopify.baseStoreURL')]).value
        access_token = store.search([('key', '=', 'hspl_shopify.access_token')]).value

        if baseURL and access_token:
            headers = {
                'X-Shopify-Access-Token': access_token,
                "Content-Type": "application/json"
            }

            if without_shopify_id_orders:
                # make POST request
                for order in without_shopify_id_orders:

                    values = self.get_export_order_values(order)

                    url = f"{baseURL}/orders.json"

                    response = requests.request(method="POST", url=url, headers=headers, data=json.dumps(values))
                    error = response.json().get("errors")

                    if response.status_code == 201:
                        response_data = response.json()

                        response_order = response_data.get("order")
                        order.with_context(skip_export_flag=True).with_user(
                            self.env.ref("hspl_shopify.shopify_user_root")).write({
                            "shopify_orders_id": response_order.get("id"),
                            "is_exported_to_shopify": True,
                        })
                    else:
                        raise UserError(
                            f"Failed to export data for order id ={order.id}. Response {response.status_code}- {error}")

            if with_shopify_id_orders:

                for order in with_shopify_id_orders:
                    values = self.get_export_order_values(order)
                    print("json.dumps(values)", json.dumps(values))

                    url = f"{baseURL}/orders/{order.shopify_orders_id}.json"
                    response = requests.request("PUT", url, headers=headers, data=json.dumps(values))
                    error = response.json().get("errors")
                    print("response.status_code", response.status_code)
                    print("error", error)
                    print("response.json()", response.json())

                    if response.status_code == 200:
                        order.with_context(skip_export_flag=True).with_user(
                            self.env.ref("hspl_shopify.shopify_user_root")).write({
                            "is_exported_to_shopify": True,
                        })
                        print("Export Success")
                    else:
                        raise UserError(
                            f"Failed to export data for order id ={order.id}. Response {response.status_code}.{error}")
        else:
            raise UserError("Improper Store Details")

    def get_export_order_values(self, order):

        if order.partner_id.shopify_customer_id == False:
            raise UserError(
                f"Export of order (id={order.id}) failed as {order.partner_id.name} is not a Shopify Product")
        line_val_list = []
        if order.order_line:
            for line in order.order_line:
                if line.product_id.shopify_variant_id == False:
                    raise UserError(
                        f"Export of order (id={order.id}) failed as {line.product_id.name} is not a Shopify Product")
                line_vals_dict = {
                    'title': line.product_id.name,
                    'price': line.price_unit,
                    'variant_id': line.product_id.shopify_variant_id,
                    'quantity': int(line.product_uom_qty),

                }

                tax_line_lst = []
                if line.tax_id:
                    for tax in line.tax_id:
                        tax_line_dict = {
                            'title': tax.tax_group_id.name,
                            'rate': tax.amount / 100
                        }
                        tax_line_lst.append(tax_line_dict)
                    line_vals_dict["tax_lines"] = tax_line_lst

                line_val_list.append(line_vals_dict)

        bill_first_name, bill_last_name = (order.partner_invoice_id.name).split(" ")
        billing_address = {
            "first_name": bill_first_name,
            "last_name": bill_last_name,
            "name": bill_first_name + " " + bill_last_name,
            "phone": order.partner_invoice_id.mobile,
            "address1": order.partner_invoice_id.street,
            "address2": order.partner_invoice_id.street2,
            "city": order.partner_invoice_id.city,
            "zip": order.partner_invoice_id.zip,
            "province": order.partner_invoice_id.state_id.name,
            "country": order.partner_invoice_id.country_id.name,
            "province_code": order.partner_invoice_id.state_id.code,
            "country_code": order.partner_invoice_id.country_id.code,
        }

        deliv_first_name, deliv_last_name = (order.partner_shipping_id.name).split(" ")
        delivery_address = {
            "first_name": deliv_first_name,
            "last_name": deliv_last_name,
            "name": deliv_first_name + " " + deliv_last_name,
            "phone": order.partner_shipping_id.mobile,
            "address1": order.partner_shipping_id.street,
            "address2": order.partner_shipping_id.street2,
            "city": order.partner_shipping_id.city,
            "zip": order.partner_shipping_id.zip,
            "province": order.partner_shipping_id.state_id.name,
            "country": order.partner_shipping_id.country_id.name,
            "province_code": order.partner_shipping_id.state_id.code,
            "country_code": order.partner_shipping_id.country_id.code,
        }

        data = {
            "order": {
                "id": order.shopify_orders_id,
                "customer": {
                    "id": order.partner_id.shopify_customer_id,
                },
                "line_items": line_val_list,
                "billing_address": billing_address,
                "shipping_address": delivery_address,
            }
        }

        return data

    def get_export_order_values_gql(self, order):
        pass
