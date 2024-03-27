from odoo import _,fields, models, api
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class LoanSalaryRule(models.Model):
    _description = 'Salary rule for Loan'
    _inherit = "hr.salary.rule"

    def create_loan_rule(self):
        category = self.env['hr.salary.rule.category'].search([('name', '=', 'Deduction')], limit=1)
        loan_register = self.env['hr.contribution.register'].search([('name', '=', 'Loan Register')], limit=1)

        if not loan_register:
            loan_register = self.env['hr.contribution.register'].create({
                'name': 'Loan Register',
                'company_id': self.env.company.id,
            })

        loan = self.env["hr.salary.rule"].search([('name', '=', "Loan")])

        if not loan:

            self.env["hr.salary.rule"].create({
                'name': 'Loan',
                'category_id': category,
                'sequence': 10,
                'register_id': loan_register,
                'company_id': self.env.company.id,
                'active': 1,
                'appears_on_payslip': 1,
                'amount_select': 'code',
                'amount_python_compute': '''result = -(self.env["loan.loan"].search([('employee', '=', payslip.employee_id.id)]).installment_amount)
    '''
            })


# from datetime import datetime
# from odoo import models, api
#
# class EmployeePayslip(models.Model):
#     _inherit = 'hr.payslip'
#
#     @api.model
#     def action_payslip_done(self):
#         print("000000000")
#         for payslip in self:
#             print("AAAAAAAAAAAAA")
#             date_start = payslip.date_from
#             print("date_start", date_start)
#         return super(EmployeePayslip, self).action_payslip_done()


# from oca_modules.payroll.models.base_browsable import BrowsableObject
#
# class Loan(BrowsableObject):
#














