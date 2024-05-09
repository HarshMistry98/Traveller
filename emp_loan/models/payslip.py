
from odoo import fields, models, api
# from .loan_menu_inherit import printcall
from .loan_menu_inherit import LoanMenuInherit



class Payslip(models.Model):
    _inherit = 'hr.payslip'
    _description = 'Description'

    def compute_sheet(self):
        res = super(Payslip, self).compute_sheet()
        records = self.env["loan.installment"].search(
            [('emi_month', '=', self.date_from.month),
             ('emi_year', '=', self.date_from.year),
             ('loan_id.employee', '=', self.employee_id.id),
             ('paid', '=', False)], limit=1)

        for record in records:
            record.paid = True
        return res

    def get_lines_dict(self):

        res = super().get_lines_dict()
        remove_key = False
        for key, line in list(res.items()):
            if line.get("code") == "EMI" and abs(line.get("total")) == 0:
                remove_key = key
        if remove_key:
            del res[remove_key]
        return res

    # def create_loan2_salary_rule(self):
    #     loan2_rule = self.env['hr.salary.rule'].search([('code', '=', 'L2')], limit=1)
    #     if not loan2_rule:
    #         loan2_rule = self.env['hr.salary.rule'].create({
    #             'amount_select': 'code',
    #             'code': 'L2',
    #             'category_id': self.env.ref('payroll.DED').id,
    #             'name': 'Loan2',
    #             'sequence': 35,
    #             'amount_python_compute': "result = -(env['loan.loan'].search([('employee.name', '=', payslip.employee_id.name), ('statusbar', '=', 'approved')], limit=1).amount)"
    #         })