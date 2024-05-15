from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    store_name = fields.Char()
    api_version = fields.Char()
    store_domain = fields.Char()
    baseStoreURL = fields.Char(string="Base URl")
    access_token = fields.Char()

