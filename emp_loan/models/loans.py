from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api


class EmployeeLoan(models.Model):
    _name = 'loan.loan'
    _description = 'Loan Granted By Complany To Employees'

    name = fields.Char(string='Loan Sequence', readonly=True)

    employee = fields.Many2one('hr.employee', "Employee", default=lambda self: self.env.user.employee_id.id)
    # readonly = True, compute = '_compute_employee'
    loan_type = fields.Selection([
        ('bike', 'Bike Loan'),
        ('car', 'Car Loan'),
        ('home', 'Home Loan'),
        ('education', 'Education Loan'),
        ('personal', 'Personal Loan')
    ])

    duration_period = fields.Integer("Duration", default=1)

    duration_type = fields.Selection([
        ('months', 'Months'),
        ('years', 'Years')
    ], default='months')

    start_date = fields.Date("Date", default=fields.Date.today)
    end_date = fields.Date("End Date", readonly=True, compute="_compute_end_date")

    amount = fields.Float("Amount")

    installment_amount = fields.Float("Installment Amount", compute="_compute_installment_amount")

    balance = fields.Float("Balance", compute="_compute_balance")

    installment_ids = fields.One2many("loan.installment", "loan_id")

    @api.model_create_multi
    def create(self, vals_list):
        records = super(EmployeeLoan, self).create(vals_list)
        for rec in records:
            seq = self.env['ir.sequence'].next_by_code('employee.loan.seq')
            rec.name = seq
            self.create_installments()
            # self.create1()
        return records

    def write(self, vals):
        if not self.name:
            seq = self.env['ir.sequence'].next_by_code('employee.loan.seq')
            vals.update({
                'name': seq
            })
        res = super(EmployeeLoan, self).write(vals)
        self.create_installments()
        # self.write1()
        return res

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        print(">>>>>>>>", domain, offset, limit, order, count)
        return super().search(domain=domain, offset=offset, limit=limit, order=order, count=count)

    @api.depends("duration_period", "duration_type", "start_date")
    def _compute_end_date(self):
        for rec in self:
            if rec.duration_period and rec.duration_type and rec.start_date:
                if rec.duration_type == 'months':
                    rec.end_date = rec.start_date + relativedelta(months=rec.duration_period)
                else:
                    rec.end_date = rec.start_date + relativedelta(years=rec.duration_period)

    @api.depends("duration_period", "duration_type", "amount")
    def _compute_installment_amount(self):
        for rec in self:
            if rec.duration_period and rec.duration_type and rec.amount:
                if rec.duration_type == 'years':
                    total_months = rec.duration_period * 12
                else:
                    total_months = rec.duration_period
                rec.installment_amount = rec.amount / total_months
            else:
                rec.installment_amount = 0

    @api.depends("duration_period", "duration_type")
    def create_installments(self):
        for rec in self:
            existing_installments = self.env["loan.installment"].search([('loan_id', '=', rec.id),('paid','=',False)])
            existing_installments.unlink()  # Remove existing installments to recalculate

            if rec.duration_period and rec.duration_type and rec.start_date:
                if rec.duration_type == 'years':
                    total_months = rec.duration_period * 12
                else:
                    total_months = rec.duration_period

                installment_amount = rec.amount / total_months

                print("Total months", total_months)
                date = rec.start_date
                for i in range(total_months):
                    self.env["loan.installment"].create({
                        'note': f"{date.year} - Monthly(12) Period #{date.month} payment on {rec.name}",
                        'pay_period': f"{date.year} - Monthly(12) Period #{date.month}",
                        'amount': installment_amount,
                        'paid': False,
                        'loan_id': rec.id,
                        'emi_date': date,
                        'emi_month': date.month,
                        'emi_year': date.year,
                    })
                    print(i)
                    date += relativedelta(months=1)

    # def create_installments(self):
    #     for rec in self:
    #         existing_installments = self.env["loan.installment"].search([('loan_id', '=', rec.id)])
    #         if not existing_installments:
    #             if rec.duration_period and rec.duration_type and rec.start_date:
    #                 if rec.duration_type == 'years':
    #                     total_months = rec.duration_period * 12
    #                 else:
    #                     total_months = rec.duration_period
    #                 print("Total months", total_months)
    #                 date = rec.start_date
    #                 for i in range(total_months):
    #                     self.env["loan.installment"].create({
    #                         'note': f"{date.year} - Monthly(12) Period #{date.month} payment on {rec.name}",
    #                         'pay_period': f"{date.year} - Monthly(12) Period #{date.month}",
    #                         'amount': rec.installment_amount,
    #                         'paid': False,
    #                         'loan_id': rec.id,
    #                         'emi_date': date,
    #                         'emi_month': date.month,
    #                         'emi_year': date.year,
    #                     })
    #                     print(i)
    #                     date += relativedelta(months=1)

    @api.depends("amount", "installment_amount")
    def _compute_balance(self):


        for rec in self:
            if rec.amount and rec.installment_amount:
                months_paid = self.env["loan.installment"].search_count([('loan_id', '=', rec.id), ('paid', '=', 1)])

                rec.balance = rec.amount - months_paid * rec.installment_amount
            else:
                rec.balance = 0


    @api.model
    def _get_default_employee(self):
        return self.env.user.employee_id

    @api.model
    def default_get(self, fields_list):
        defaults = super(EmployeeLoan, self).default_get(fields_list)
        if 'employee' in fields_list:
            defaults['employee'] = self._get_default_employee()
        return defaults

