from odoo import fields
from odoo.addons.payroll.models.base_browsable import BrowsableObject

class Loan(BrowsableObject):
    def get_installment(self):
        installment = self.env["loan.installment"]
        emi_records = installment.search([("loan_id.employee", "=", self.employee_id.id), ('paid', '=', False)],
                                         limit=1)
        return installment
