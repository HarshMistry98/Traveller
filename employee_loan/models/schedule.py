from odoo import fields, models, api


class LoanInstallment(models.Model):
    _name = 'loan.installment'
    _description = 'Loan Installment'

    note = fields.Char("Note")

    pay_period = fields.Char("Pay Period")

    paid = fields.Boolean("Paid")

    amount = fields.Float("Installment Amount", required=True)

    emi_date = fields.Date("EMI Date")
    emi_month = fields.Integer("Month")
    emi_year = fields.Integer("Year")

    loan_id = fields.Many2one('loan.loan', string='Loan', ondelete='cascade')

