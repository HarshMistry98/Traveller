from odoo import fields, models, api
import requests
import json

from odoo.exceptions import UserError


class customersDetails(models.Model):
    _inherit = 'res.partner'
    _description = 'Customer Details'

    shopify_customer_id = fields.Char("Shopify ID")
    is_shopify_customer = fields.Boolean("Shopify Customer", default=False)
    is_exported_to_shopify = fields.Boolean("Exported to Shopify")

    shopify_customer_status = fields.Selection([
        ('enabled', 'Enable'),
        ('disabled', 'Disable'),
        ('invited', 'Invited'),
        ('rejected', 'Rejected'),
    ], default='disabled', required=True)

    def write(self, vals):
        if not self.env.context.get('skip_export_flag'):
            vals.update({
                "is_exported_to_shopify": False,
            })
        res = super(customersDetails, self).write(vals)
        return res

    def update_customers(self, response_data=False):
        partners = self.env['res.partner']
        print("1111", response_data)
        if not response_data:
            store = self.env['ir.config_parameter']

            baseURL = store.search([('key', '=', 'hspl_shopify.baseStoreURL')]).value
            access_token = store.search([('key', '=', 'hspl_shopify.access_token')]).value

            if baseURL and access_token:
                url = f"{baseURL}/customers.json"

                payload = {}
                headers = {
                    'X-Shopify-Access-Token': access_token,
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                if response.status_code == 200:
                    response_customer_data = response.json()
                    customers = response_customer_data.get('customers')
                else:
                    print(f"Error: {response.status_code}")
                    raise UserError(f"Error: {response.status_code}")
            else:
                raise UserError("Improper Store Details")

        else:
            customers = [response_data]
        print("response_data", response_data)
        print("customers", customers)
        for customer in customers:
            values = self.get_customer_values(customer)
            partner_exist = partners.search([('shopify_customer_id', '=', values['shopify_customer_id'])])
            try:
                if partner_exist:
                    partner_exist.with_context(skip_export_flag=True).write(values)
                else:
                    partners.create(values)
            except Exception as e:
                raise e

    def get_customer_values(self, customer):
        values = {
            'is_exported_to_shopify': True,
            'is_shopify_customer': True,
            'shopify_customer_id': str(customer.get("id")),
            'shopify_customer_status': customer.get("state"),
            'email': customer.get("email"),
            'name': customer.get("first_name") + ' ' + customer.get("last_name"),
            'mobile': customer.get("phone"),
            'street': customer.get("addresses")[0].get('address1'),
            'street2': customer.get("addresses")[0].get('address2'),
            'city': customer.get("addresses")[0].get('city'),
            'zip': customer.get("addresses")[0].get('zip'),
        }
        state_name = customer.get("addresses")[0].get('province')
        country_name = customer.get("addresses")[0].get('country')
        state_id = False
        country_id = False
        if state_name:
            state = self.env['res.country.state'].search([('name', '=ilike', state_name)], limit=1)
            if state:
                state_id = state.id
        if country_name:
            country = self.env['res.country'].search([('name', '=ilike', country_name)], limit=1)
            if country:
                country_id = country.id
        values.update({
            'state_id': state_id,
            'country_id': country_id,
        })
        print("values----->", values)
        return values

    def export_customers(self):

        without_shopify_id_customers = self.env['res.partner'].search([("shopify_customer_id", "=", False),
                                                                       ("is_exported_to_shopify", "=", False),
                                                                       ("is_shopify_customer", "=", True), ])
        # If the customer do not have Shopify ID so that customer is not present on Shopify
        # therefore during export we have to create the customer

        with_shopify_id_customers = self.env['res.partner'].search([("shopify_customer_id", "!=", False),
                                                                    ("is_exported_to_shopify", "=", False),
                                                                    ("is_shopify_customer", "=", True)])
        # If the customer have Shopify ID so that customer is  present on Shopify
        # therefore during export we have to update the customer

        store = self.env['ir.config_parameter']
        baseURL = store.search([('key', '=', 'hspl_shopify.baseStoreURL')]).value
        access_token = store.search([('key', '=', 'hspl_shopify.access_token')]).value

        if baseURL and access_token:
            headers = {
                'X-Shopify-Access-Token': access_token,
                "Content-Type": "application/json"
            }

            if without_shopify_id_customers:
                # make POST request
                for customer in without_shopify_id_customers:

                    values = self.get_export_customer_values(customer)

                    url = f"{baseURL}/customers.json"

                    response = requests.request(method="POST", url=url, headers=headers, data=json.dumps(values))
                    error = response.json().get("errors")

                    if response.status_code == 201:
                        response_data = response.json()

                        response_customer = response_data.get("customer")
                        customer.with_context(skip_export_flag=True).write({
                            "shopify_customer_id": response_customer.get("id"),
                            "is_exported_to_shopify": True,
                        })
                    else:
                        raise UserError(
                            f"Failed to export data for customer id ={customer.id}. Response {response.status_code}- {error}")

            if with_shopify_id_customers:

                for customer in with_shopify_id_customers:
                    values = self.get_export_customer_values(customer)

                    url = f"{baseURL}/customers/{customer.shopify_customer_id}.json"
                    response = requests.request("PUT", url, headers=headers, data=json.dumps(values))
                    error = response.json().get("errors")

                    if response.status_code == 200:
                        customer.with_context(skip_export_flag=True).write({
                            "is_exported_to_shopify": True,
                        })
                    else:
                        raise UserError(
                            f"Failed to export data for customer id ={customer.id}. Response {response.status_code}.{error}")
        else:
            raise UserError("Improper Store Details")

    def get_export_customer_values(self, customer):

        first_name, last_name = customer.name.split(" ")
        tag_vals = ','.join(str(tag.name) for tag in customer.category_id) if customer.category_id else ''
        data = {
            "customer": {
                "first_name": first_name,
                "last_name": last_name,
                "email": customer.email,
                "phone": customer.mobile,
                'state': customer.shopify_customer_status,
                "tags": tag_vals,
                "addresses": [
                    {
                        "address1": customer.street if customer.street else "",
                        "address2": customer.street2 if customer.street else "",
                        "city": customer.city if customer.city else "",
                        "phone": customer.phone if customer.phone else "",
                        "zip": customer.zip if customer.zip else "",
                        'first_name': first_name,
                        'last_name': last_name,
                        "province": customer.state_id.name if customer.state_id else "",
                        "country": customer.country_id.name if customer.country_id else "",
                    }
                ],
            }
        }
        return data

    def enable_shopify_customer(self):
        print("Enabling")
        print(self._context)

        for customer_id in self._context.get("active_ids"):
            customer = self.env['res.partner'].browse(customer_id)
            store = self.env['ir.config_parameter']
            baseURL = store.get_param('hspl_shopify.baseStoreURL')
            access_token = store.get_param('hspl_shopify.access_token')
            if baseURL and access_token:
                url = f"{baseURL}/customers/{customer.shopify_customer_id}.json"
                print("url",url)
                headers = {
                    'X-Shopify-Access-Token': access_token,
                }
                customer_values = {
                    "customer": {
                        "id": int(customer.shopify_customer_id),
                        "state": "enabled"
                    }
                }
                print("json.dumps(customer_values)", json.dumps(customer_values, indent=4))
                response = requests.request("PUT", url=url, headers=headers, data=json.dumps(customer_values))

                if response.status_code == 200:
                    customer_response = response.json().get('customer')

                    customer.write({
                        "shopify_customer_status": customer_response.get("state"),
                    })
                else:
                    print(f"Error: {response.status_code} {response.text}")
                    raise UserError(f"Error: {response.status_code} {response.text}")
            else:
                raise UserError("Improper Store Details")


    def disable_shopify_customer(self):
        print("Disabling")
        print(self._context)

        for customer_id in self._context.get("active_ids"):
            customer = self.env['res.partner'].browse(customer_id)
            store = self.env['ir.config_parameter']
            baseURL = store.get_param('hspl_shopify.baseStoreURL')
            access_token = store.get_param('hspl_shopify.access_token')
            if baseURL and access_token:
                url = f"{baseURL}/customers/{customer.shopify_customer_id}.json"
                print("url",url)
                headers = {
                    'X-Shopify-Access-Token': access_token,
                }
                customer_values = {
                    "customer": {
                        "id": int(customer.shopify_customer_id),
                        "state": "disabled"
                    }
                }
                print("json.dumps(customer_values)", json.dumps(customer_values, indent=4))
                response = requests.request("PUT", url=url, headers=headers, data=json.dumps(customer_values))

                if response.status_code == 200:
                    customer_response = response.json().get('customer')

                    customer.write({
                        "shopify_customer_status": customer_response.get("state"),
                    })
                else:
                    print(f"Error: {response.status_code} {response.text}")
                    raise UserError(f"Error: {response.status_code} {response.text}")
            else:
                raise UserError("Improper Store Details")
