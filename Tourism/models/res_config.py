from odoo import api, fields, models


class res_company(models.Model):
    _inherit = "res.company"

    need_transport = fields.Boolean("Transport")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one("res.company")
    need_transport = fields.Boolean("Transport", readonly=False, relatef="company_id.need_transport")
