import requests

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    store_name = fields.Char(string="Store Name", config_parameter='hspl_shopify.store_name')

    api_version = fields.Char(string="API Version", config_parameter='hspl_shopify.api_version',
                              help="Format according to release month and year YYYY-MM ")

    baseStoreURL = fields.Char(string="Base URl", readonly=1, compute="_compute_baseStoreURL",
                               config_parameter='hspl_shopify.baseStoreURL',
                               default="https://your-store-name.myshopify.com/admin/api/api-version")
    
    store_domain = fields.Char(string="Store Domain",
                               config_parameter='hspl_shopify.store_domain')

    access_token = fields.Char(string="Access Token", config_parameter='hspl_shopify.access_token',
                               help="Accesss Token generated for store")

    @api.depends("store_name", "api_version")
    def _compute_baseStoreURL(self):
        for rec in self:
            rec.baseStoreURL = f"https://{rec.store_name}.myshopify.com/admin/api/{rec.api_version}"


    def test_shopify_connection(self):
        store = self.env['ir.config_parameter']

        baseURL = store.search([('key', '=', 'hspl_shopify.baseStoreURL')]).value
        access_token = store.search([('key', '=', 'hspl_shopify.access_token')]).value

        if baseURL and access_token:
            payload = {}
            headers = {
                'X-Shopify-Access-Token': access_token,
            }
            response = requests.request("GET", baseURL, headers=headers, data=payload)
            if response.status_code == 200:

                message = _("Connection Test Successful!")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': message,
                        'type': 'success',
                        'sticky': False,
                    }
                }

            else:
                message = _(f"Connection Test Failed!  Status Code {response.status_code}")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': message,
                        'type': 'danger',
                        'sticky': False,
                    }
                }

