import json

import requests

from odoo import fields, models, api
from odoo.exceptions import UserError


class StockWarehouse(models.Model):
    _inherit = 'stock.quant'
    _description = 'Stock Quant'

    location_id = fields.Many2one(domain="[('shopify_location', '=', True)]")

    def export_inventory(self):
        product_variants = self.env['product.product'].search([("is_shopify_variant", "=", True)])

        for product_variant in product_variants:
            stocks = self.search([("product_id", "=", product_variant.id),
                                  ("location_id.is_shopify_location", "=", True)])
            for stock in stocks:
                print("stock location", stock.location_id.name)
                self.update_stock(stock.warehouse_id.shopify_warehouse_id,product_variant.shopify_inventory_id,stock.available_quantity,product_variant)

    def update_stock(self,location_id,inventory_item_id,available,product_variant):
        store = self.env['ir.config_parameter']
        baseURL = store.search([('key', '=', 'hspl_shopify.baseStoreURL')]).value
        access_token = store.search([('key', '=', 'hspl_shopify.access_token')]).value

        if baseURL and access_token:
            headers = {
                'X-Shopify-Access-Token': access_token,
                "Content-Type": "application/json"
            }

            values = {
                "location_id": int(location_id),
                "inventory_item_id": int(inventory_item_id),
                "available": int(available),
            }
            print("values",values)

            url = f"{baseURL}/inventory_levels/set.json"

            response = requests.request(method="POST", url=url, headers=headers, data=json.dumps(values))
            if response.status_code == 200:
                print(f"Product Variant {product_variant.name} Exported")
            if not response.status_code == 200:
                error = response.json().get("errors", " ")
                raise UserError(
                    f"Failed to export inventory for product variant id ={product_variant.name}. Response {response.status_code}- {error}")
        else:
            raise UserError("Improper Store Details")
