import requests

from odoo import fields, models, api
from odoo.exceptions import UserError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    _description = 'Stock Warehouse'

    shopify_warehouse_id = fields.Char(string="Shopify Warehouse ID")
    is_shopify_warehouse = fields.Boolean(string="Shopify Warehouse")

    def update_warehouses(self, response_data=False):
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
                    warehouses = response_locations_data.get('locations')
                else:
                    print(f"Error: {response.status_code}")
                    raise UserError(f"Error: {response.status_code} ")
            else:
                raise UserError("Improper Store Details")

        else:
            warehouses = [response_data]

        for warehouse in warehouses:
            values = self.get_warehouses_values(warehouse)
            current_warehouse = self.env['stock.warehouse'].search(
                [('shopify_warehouse_id', '=', values['shopify_warehouse_id'])])
            try:
                if current_warehouse:
                    current_warehouse.write(values)
                else:
                    current_warehouse = self.env['stock.warehouse'].create(values)
            except Exception as e:
                raise e
            print("current_warehouse", current_warehouse)

            locations_of_warehouse = self.env['stock.location'].search([("warehouse_id", "=", current_warehouse.id)])
            print("locations_of_warehouse", locations_of_warehouse)
            for location in locations_of_warehouse:
                location.is_shopify_location = True

    def get_warehouses_values(self, warehouse):

        acronym = ''.join(word[0].upper() for word in warehouse.get("name").split())
        values = {
            "shopify_warehouse_id": warehouse.get("id"),
            "is_shopify_warehouse": True,
            "name": warehouse.get("name"),
            "code": acronym,
            "company_id": self.env.company.id,
        }

        return values
