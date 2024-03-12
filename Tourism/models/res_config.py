from odoo import api, fields, models


class res_company(models.Model):
    _inherit = "res.company"

    is_staff = fields.Boolean("Staff",  )
    is_department = fields.Boolean("Department" )

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_staff = fields.Boolean("Staff",related='company_id.is_staff',readonly=False)
    is_department = fields.Boolean("Department", readonly=False,config_parameter='Tourism.profiling_enabled_until')
