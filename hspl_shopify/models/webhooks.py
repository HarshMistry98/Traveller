import json

import requests

from odoo import fields, models, api
from odoo.exceptions import UserError


class Webhooks(models.Model):
    _name = 'shopify.webhooks'
    _description = 'Description'

    webhook_id = fields.Char('Webhook ID', readonly=True)
    topic = fields.Char('Topic', required="True")
    # address = fields.Char('Address')
    target_address = fields.Char('Target Address', compute="_compute_target_address")
    format = fields.Char("Format", default='json')
    published = fields.Boolean("Publish on Shopify", readonly=True)

    @api.depends("target_address")
    def _compute_target_address(self):
        print("Target changing")
        web_base_url = self.env['ir.config_parameter'].get_param('hspl_shopify.store_domain')
        if not web_base_url:
            web_base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        for rec in self:
            target_address = web_base_url + "/shopify/webhook/" + rec.topic
            rec.target_address = target_address

    # @api.onchange("target_address")
    # def _onchange_target_address(self):
    #     print("on chanchanging address")
    def publish_webhook(self):
        store = self.env['ir.config_parameter']

        domain_url = store.get_param('hspl_shopify.store_domain')

        baseURL = store.get_param('hspl_shopify.baseStoreURL')
        access_token = store.get_param('hspl_shopify.access_token')

        if baseURL and access_token and domain_url:
            url = baseURL + '/webhooks.json'
            payload = {
                "webhook": {
                    "topic": self.topic,
                    "address": str(domain_url + "/shopify/webhook/" + self.topic),
                    "format": self.format
                }
            }
            headers = {
                "X-Shopify-Access-Token": access_token,
                "Content-Type": "application/json",
            }

            response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            if response.status_code in [200, 201]:
                response_data = response.json()
                if response_data and 'webhook' in response_data:
                    webhooks = response_data.get('webhook')

                    values = {
                        "webhook_id": webhooks.get('id'),
                        "target_address": webhooks.get('address'),
                        "published": True,
                    }
                    self.write(values)
                else:
                    UserError("No webhooks found in response.")
            else:
                if response.text:
                    try:
                        error_message = response.json().get('errors')
                    except ValueError:
                        error_message = response.text

                else:
                    error_message = "Empty response"
                raise UserError(f"Error: {response.status_code} --> {error_message} ")
        else:
            raise UserError("Invalid URL or Access Token or Domain URL. Kindly check the connection in Settings")

    #
    def unpublish_webhook(self):

        store = self.env['ir.config_parameter']

        baseURL = store.get_param('hspl_shopify.baseStoreURL')
        access_token = store.get_param('hspl_shopify.access_token')

        if baseURL and access_token:
            url = f'{baseURL}/webhooks/{self.webhook_id}.json'

            payload = {}
            headers = {
                'X-Shopify-Access-Token': access_token,
            }

            response = requests.request("DELETE", url, headers=headers)
            if response.status_code == 200:
                self.write({
                    "webhook_id": False,
                    "published": False,
                })
            else:
                if response.text:
                    try:
                        error_message = response.json().get('errors')
                    except ValueError:
                        error_message = response.text
                else:
                    error_message = "Empty response"
                raise UserError(f"Error: {response.status_code} --> {error_message} ")
