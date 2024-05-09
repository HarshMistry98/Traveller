from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'hr.employee'
    _description = 'Description'

    loan_id = fields.Many2one('loan.loan', string='Loan', ondelete='cascade', compute='compute_loan')

    @api.depends("name")
    def compute_loan(self):
        for rec in self:
            loan = self.env["loan.loan"]
            is_loan = loan.search([('employee', '=', rec.id)], limit=1)

            if is_loan:
                rec.loan_id = is_loan.id
            else:
                rec.loan_id = None



