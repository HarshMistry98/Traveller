from odoo import fields, models, api
import requests

class customersDetails(models.Model):
    _inherit = 'res.partner'
    _description = 'Customer Details'

    shopify_customer_id = fields.Char("Shopify ID")
    # def update_customers(self, response_data):
    #     for rec in self:
    #         partners = self.env['res.partner']
    #         list_customers = response_data.get("customers")
    #         for customer in list_customers:
    #             values = {
    #                 'shopify_customer_id': str(customer.get("id")),
    #                 'email': customer.get("email"),
    #                 'name': customer.get("first_name") + ' ' + customer.get("last_name"),
    #                 'mobile': customer.get("phone"),
    #                 'street': customer.get("addresses")[0].get('address1'),
    #                 'street2': customer.get("addresses")[0].get('address2'),
    #                 'city': customer.get("addresses")[0].get('city'),
    #                 'zip': customer.get("addresses")[0].get('zip'),
    #             }
    #             # Determine state and country based on received data
    #             state_name = customer.get("addresses")[0].get('province')
    #             country_name = customer.get("addresses")[0].get('country')
    #
    #             state_id = False
    #             country_id = False
    #
    #             if state_name:
    #                 state = rec.env['res.country.state'].search([('name', '=ilike', state_name)], limit=1)
    #                 if state:
    #                     state_id = state.id
    #
    #             if country_name:
    #                 country = rec.env['res.country'].search([('name', '=ilike', country_name)], limit=1)
    #                 if country:
    #                     country_id = country.id
    #
    #             values.update({
    #                 'state_id': state_id,
    #                 'country_id': country_id,
    #             })
    #             print(values)
    #
    #             partner_exist = partners.search([('shopify_customer_id', '=', values['shopify_customer_id'])])
    #             try:
    #                 if partner_exist:
    #                     partner_exist.write(values)
    #                     print("Partner Updated")
    #                 else:
    #                     partners.create(values)
    #                     print("Partner Created")
    #             except Exception as e:
    #                 raise e

