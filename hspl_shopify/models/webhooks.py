import json

import requests

from odoo import fields, models, api
from odoo.exceptions import UserError


class Webhooks(models.Model):
    _name = 'shopify.webhooks'
    _description = 'Description'

    webhook_id = fields.Char('Webhook ID', readonly=True)
    topic = fields.Char('Topic')
    # address = fields.Char('Address')
    target_address = fields.Char('Target Address')
    format = fields.Char("Format", default='json')

    @api.model_create_multi
    def create(self, vals_list):
        # records = super(Webhooks, self).create(vals_list)
        print('vals_list', vals_list)

        store = self.env['ir.config_parameter']
        domain_url = store.search([('key', '=', 'hspl_shopify.store_domain')]).value

        print('domain_url', domain_url)

        baseURL = store.search([('key', '=', 'hspl_shopify.baseStoreURL')]).value
        access_token = store.search([('key', '=', 'hspl_shopify.access_token')]).value

        if baseURL and access_token and domain_url:
            url = baseURL + '/webhooks.json'
            payload = {
                "webhook": {
                    "topic": str(vals_list[0].get('topic')),
                    "address": str(domain_url + "/shopify/webhook/" + vals_list[0].get('topic')),
                    "format": str(vals_list[0].get('format'))
                }
            }
            print("url", url)
            print("payload", payload)
            headers = {
                "X-Shopify-Access-Token": access_token,
                "Content-Type": "application/json",
            }
            print("headers", headers)

            response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            if response.status_code in [200, 201]:
                response_data = response.json()
                if response_data and 'webhook' in response_data:
                    webhooks = response_data.get('webhook')

                    # for webhook in webhooks:
                    values = {
                        "webhook_id": webhooks.get('id'),
                        "target_address": webhooks.get('address'),
                    }
                    webhook_exist = self.search([('webhook_id', '=', webhooks.get('id'))], limit=1)
                    if not webhook_exist:
                        vals_list[0].update(values)
                        print("Paachi vals_list", vals_list)
                        print("written")
                    else:
                        webhook_exist.write(values)
                        print("updated")

                else:
                    print("No webhooks found in response.")
            else:
                print(f"Error: {response.status_code}")
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

        records = super(Webhooks, self).create(vals_list)
        return records

    def unlink(self):
        for rec in self:

            store = self.env['ir.config_parameter']

            baseURL = store.search([('key', '=', 'hspl_shopify.baseStoreURL')]).value
            access_token = store.search([('key', '=', 'hspl_shopify.access_token')]).value

            if baseURL and access_token:
                url = f'{baseURL}/webhooks/{rec.webhook_id}.json'

                payload = {}
                headers = {
                    'X-Shopify-Access-Token': access_token,
                }

                response = requests.request("DELETE", url, headers=headers)
        return super(Webhooks, self).unlink()
