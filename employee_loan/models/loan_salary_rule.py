from ...oca_modules.payroll.tests.common import TestPayslipBase
from odoo import _, fields, models, api
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
from odoo.tests.common import TransactionCase
from ...employee_loan.models.browsable import Loan


class LoanRule(TestPayslipBase):
    def setUp(self):
        super(LoanRule, self).setUp()

        self.register_loan = self.PayrollStructure.create({
            'name': 'Loan Register',
            'company_id': self.env.company.id,
        })

        self.rule_loan = self.SalaryRule.create({
            'name': 'Loan',
            'code': 'EMI',
            'sequence': 10,
            'category_id': self.categ_ded.id,
            "condition_select": "none",
            'register_id': self.register_loan,
            'company_id': self.env.company.id,
            'active': 1,
            'appears_on_payslip': 1,
            'amount_select': 'code',
            'amount_python_compute': '''result = -Loan.get_installment()['emi_amount']'''
        })


class LoanSalarySlip(models.Model):
    _inherit = 'hr.payslip'

    def _get_baselocaldict(self, contracts):
        localdict = super(LoanSalarySlip, self)._get_baselocaldict(contracts)

        # Add your key-value pair to the localdict
        localdict['loan'] = Loan(self.employee_id.id, self, self.env)
        print("////////////////////", localdict)

        return localdict






