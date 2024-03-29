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
        # dater = self.date_from
        # daterend = self.date_to
        # print(dater)
        # print(daterend)

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

    @api.depends('dynamic_filtered_payslip_lines.total_amount')
    def _compute_visible_rows(self):
        for record in self:
            filtered_records = record.dynamic_filtered_payslip_lines.filtered(lambda x: x.total_amount != 0)
            record.dynamic_filtered_payslip_lines = [(6, 0, filtered_records.ids)]