from odoo import models, fields, api


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    def _compute_rule(self, localdict):
        result = super(HrSalaryRule, self)._compute_rule(localdict)

        # Check if the result is zero
        if result == 0:
            return False

        return result
