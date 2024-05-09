from odoo import fields, models, api
from odoo.exceptions import UserError


class LoanMenuInherit(models.Model):
    # _name = 'loan.menu.inherit'
    _inherit = ['loan.loan']
    # _inherit = ["loan.loan","mail.thread"]

    _description = 'Add status bar for Loan menu so the modle of loan.loan not effect with this '

    statusbar=fields.Selection([('requirement','Requirement'),
                                ('submitted','Submitted'),
                                ('approved','Approved'),
                                ('cancle','Cancel')],default='requirement')

    def button_cancel(self):
        self.statusbar='cancle'
        print("cancel exicuted")
        # self.printcall()

    def button_apply(self):
        self.statusbar='submitted'
        print("apply exicuted")

    def button_approve(self):
        self.statusbar='approved'
        print("approved exicuted")


    # def chek_approval(self):
    #     # res = self.env['loan.loan'].search('employee')
    #     # res = self.env['loan.loan'].statusbar
    #     # print('--------------------------------->????', res)
    #     self.printcall()
    #     if self.statusbar=='approved':
    #         print('--------------------------------->yes')
    #     else:
    #         print('--------------------------------->NO')
    #
    #
    #         # print('--------------------------------->????', res)
    #
    #     # if self.statusbar =='approved':
    #     #     print("------------>yes is approved")
    #     # else:
    #     #     print("------------>notis not  is approved")

    def printcall(self):
        print("========================================>hello this call from loan.loan class ")
        res=self.env['loan.loan'].search([(('employee.name', '=', self.employee.name))])
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@',res)
        res_status = self.env['loan.loan'].search([('statusbar', '=', 'approved')])
        if res_status and res:
            print("Yes, there are approved loan records")
        else:
            print("No approved loan records")




    def unlink(self):
        for record in self:
            if record.statusbar in ['approved', 'submitted']:
                raise UserError("Cannot delete records with status 'approved' or 'submitted'")
        return super(LoanMenuInherit, self).unlink()