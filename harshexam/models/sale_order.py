from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    priority = fields.Selection([
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ], string="Priority", required= True)
