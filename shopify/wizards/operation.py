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
                    data = response.json()
                else:
                    print(f"Error: {response.status_code}")

                operation_for = data


            else:
                raise UserError("Improper Store Details")

        except Exception as e:
            raise e
