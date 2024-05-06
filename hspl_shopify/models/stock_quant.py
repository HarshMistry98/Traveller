from odoo import fields, models, api


class StockWarehouse(models.Model):
    _inherit = 'stock.quant'
    _description = 'Stock Quant'

    def export_inventory(self):
        pass
