from odoo import fields, models, api
import requests

class CustomerDetails(models.Model):
    _inherit = 'res.partner'
    _description = 'Customer Details'

    def updateCustomer(self):

        store = self.env['ir.config_parameter']

        baseURL = store.shopify.baseStoreURL
        url = f"{baseURL}/customers.json"

        access_token = store.shopify.access_token

        payload = {}
        headers = {
            'X-Shopify-Access-Token': access_token,
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)
