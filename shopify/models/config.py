from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    store_name = fields.Char(string="Store Name", config_parameter='shopify.store_name')

    api_version = fields.Char(string="API Version", config_parameter='shopify.api_version',
                              help="Format according to release month and year YYYY-MM ")

    baseStoreURL = fields.Char(string="Base URl", readonly=1, compute="_compute_baseStoreURL",
                               config_parameter='shopify.baseStoreURL',
                               default="https://your-store-name.myshopify.com/admin/api/api-version")

    access_token = fields.Char(string="Access Token", config_parameter='shopify.access_token',
                                help="Accesss Token generated for store")

    @api.depends("store_name", "api_version")
    def _compute_baseStoreURL(self):
        for rec in self:
            rec.baseStoreURL = f"https://{rec.store_name}.myshopify.com/admin/api/{rec.api_version}"
