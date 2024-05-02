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

    def action_import_data(self, job_for=False):

        try:
            store = self.env['ir.config_parameter']
            operation_for = job_for if job_for else self.operation_for

            baseURL = store.search([('key', '=', 'hspl_shopify.baseStoreURL')]).value
            access_token = store.search([('key', '=', 'hspl_shopify.access_token')]).value

            if baseURL and access_token:
                url = f"{baseURL}/{operation_for}.json"

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

                operatefunc = f"update_{operation_for}"
                # print(">>>>>>>",type(operatefunc))
                #
                #
                # getattr(self, operatefunc)(response_data)

                if operation_for == 'customers':
                    operateClass = self.env['res.partner']
                elif operation_for == 'products':
                    operateClass = self.env['product.template']
                elif operation_for == 'orders':
                    operateClass = self.env['sale.order']

                getattr(operateClass,operatefunc)(response_data)

            else:
                raise UserError("Improper Store Details")

        except Exception as e:
            raise e

    def action_export_data(self):
        print("Exporting")

        operation_for = self.operation_for

        operatefunc = f"export_{operation_for}"

        if operation_for == 'customers':
            operateClass = self.env['res.partner']
        elif operation_for == 'products':
            operateClass = self.env['product.template']
        elif operation_for == 'orders':
            operateClass = self.env['sale.order']

        export_data = getattr(operateClass, operatefunc)()