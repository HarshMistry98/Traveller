from odoo import fields, models, api


class Payslip(models.Model):
    _inherit = 'hr.payslip'
    _description = 'Description'

    def compute_sheet(self):
        res = super(Payslip, self).compute_sheet()

        print("res=========", res)

        records = self.env["loan.installment"].search(
            [('loan_id.employee', '=', self.employee_id.id), ('paid', '=', False)], limit=1)

        for records in records:
            records.paid = True

        return res
