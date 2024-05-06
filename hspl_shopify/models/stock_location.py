import requests

from odoo import fields, models, api
from odoo.exceptions import UserError


class StockWarehouse(models.Model):
    _inherit = 'stock.location'
    _description = 'Stock Location'

    shopify_location_id = fields.Char(string="Shopify Location ID")
    is_shopify_location = fields.Boolean(string="Shopify Location")
    
    def update_locations(self, response_data=False):
        print("Warehouse import")
        if not response_data:
            store = self.env['ir.config_parameter']

            baseURL = store.search([('key', '=', 'hspl_shopify.baseStoreURL')]).value
            access_token = store.search([('key', '=', 'hspl_shopify.access_token')]).value

            if baseURL and access_token:
                url = f"{baseURL}/locations.json"

                payload = {}
                headers = {
                    'X-Shopify-Access-Token': access_token,
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                if response.status_code == 200:
                    response_locations_data = response.json()
                    locations = response_locations_data.get('locations')
                else:
                    print(f"Error: {response.status_code}")
                    raise UserError(f"Error: {response.status_code} ")
            else:
                raise UserError("Improper Store Details")

        else:
            locations = [response_data]

        for location in locations:
            values = self.get_location_values(location)
            location_exist = self.env['stock.location'].search([('shopify_location_id', '=', values['shopify_location_id'])])
            try:
                if location_exist:
                    location_exist.write(values)
                else:
                    self.env['stock.location'].create(values)
            except Exception as e:
                raise e
        
    def get_location_values(self,location):

        values = {
            "shopify_location_id": location.get("id"),
            "is_shopify_location": True,
            "name": location.get("name"),
            "company_id": self.env.company.id,
        }

        return values
