from odoo import fields, models, api, SUPERUSER_ID


class ResGroups(models.Model):
    _inherit = 'res.groups'
    _description = 'Res Groups'

    @api.model_create_multi
    def create(self, vals_list):
        shopifybot_user = self.env.ref("hspl_shopify.shopify_user_root")

        if vals_list.get("users") and SUPERUSER_ID in vals_list.get(
                "users") and shopifybot_user.id not in vals_list.get("users"):
            vals_list['users_id'] = (vals_list.get('users_id')) + [(4, shopifybot_user.id)]

        return super(ResGroups, self).create(vals_list)

    def write(self, vals):
        shopifybot_user = self.env.ref("hspl_shopify.shopify_user_root")

        if vals.get("users") and SUPERUSER_ID in vals.get("users") and shopifybot_user.id not in vals.get("users"):
            vals['users_id'] = (vals.get('users_id')) + [(4, shopifybot_user.id)]

        return super(ResGroups, self).write(vals)
