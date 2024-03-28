from ...oca_modules.payroll.models.base_browsable import BrowsableObject


class Loan(BrowsableObject):


    def get_installment(self):
        installment = self.env["loan.installment"]
        emi_record = installment.search([("loan_id.employee", "=", self.employee_id.id),('paid', '=', False)], limit=1)

        values = {
            'installment_id': emi_record.id if emi_record else False,
            'emi_amount': emi_record.amount if emi_record else 0.0,
        }
        return values
