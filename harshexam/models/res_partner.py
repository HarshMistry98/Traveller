from odoo import fields, models, api
from odoo.exceptions import UserError


class ModelName(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner'

    @api.constrains("phone")
    def check_phone_length(self):
        for rec in self:
            if len(rec.phone) != 10:
                raise UserError(" Phone should be of 10 digits only")

    @api.onchange("phone")
    def _onchange_format_phone(self):
        for rec in self:
            phone = self.phone
            formatted_phone = ""
            for i in phone:
                print("Digit", i)
                print("Index", phone.index(i))
                if phone.index(i) in [3, 6] and phone.index(i) > 0:
                    formatted_phone += "-"
                formatted_phone += i
                print("formatted_phone", formatted_phone)

            rec.phone = formatted_phone
