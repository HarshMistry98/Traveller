import requests

from odoo import models, fields
from odoo.exceptions import UserError


class operationImport(models.TransientModel):
    _name = 'shopify.operation'
    _description = 'Importing the data'

    operation_for = fields.Selection([
        ('customers', 'Customer'),
        ('products', 'Product'),
        ('orders', 'Orders'),
        ('warehouses', 'Warehouses'),
        ('inventory', 'Inventory'),
    ], string="Operation", default="customers")

    def action_import_data(self, job_for=False):

        operation_for = job_for if job_for else self.operation_for

        operatefunc = f"update_{operation_for}"

        if operation_for == 'customers':
            operateClass = self.env['res.partner']
        elif operation_for == 'products':
            operateClass = self.env['product.template']
        elif operation_for == 'orders':
            operateClass = self.env['sale.order']
        elif operation_for == 'warehouses':
            operateClass = self.env['stock.warehouse']
        elif operation_for == 'inventory':
            raise UserError("Inventory cannot be import. Only Exported")
        else:
            raise UserError("Select the valid operation")

        getattr(operateClass, operatefunc)()

    def action_export_data(self):

        operation_for = self.operation_for

        operatefunc = f"export_{operation_for}"

        if operation_for == 'customers':
            operateClass = self.env['res.partner']
        elif operation_for == 'products':
            operateClass = self.env['product.template']
        elif operation_for == 'orders':
            operateClass = self.env['sale.order']
        elif operation_for == 'inventory':
            operateClass = self.env['stock.quant']
        elif operation_for == "warehouses":
            raise UserError("You cannot export Warehouses.")
        else:
            raise UserError("Select the valid operation")

        getattr(operateClass, operatefunc)()
