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
                # print(">>>>>>>",type(operatefunc))
                #
                #
                # getattr(self, operatefunc)(response_data)

                if self.operation_for == 'customers':
                    operateClass = self.env['res.partner']
                elif self.operation_for == 'products':
                    operateClass = self.env['product.template']
                elif self.operation_for == 'orders':
                    operateClass = self.env['sale.order']

                getattr(operateClass,operatefunc)(response_data)

            else:
                raise UserError("Improper Store Details")

        except Exception as e:
            raise e