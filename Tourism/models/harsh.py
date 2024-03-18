from io import BytesIO

import xlsxwriter

from odoo import models, fields, api
from odoo.exceptions import UserError


class Wizard_for_print(models.TransientModel):
    _name = 'travel.print_report'
    _description = 'Print selected sales orders into pdf and xlsx'

    selected_orders = fields.Many2many("sale.order", string="Orders")

    @api.model
    def default_get(self, fields):
        res = super(Wizard_for_print, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        if active_ids:
            res['selected_orders'] = [(6, 0, active_ids)]
            print(res)
        return res

    def action_pdf(self):
        report = self.env.ref("sale.action_report_saleorder")
        return report.report_action(self.selected_orders.ids)

    def action_xlsx(self):
        export_data = super(Wizard_for_print, self).export_data(self.selected_orders.ids)
        return export_data


class PrintReport(models.Model):
    # _name = 'travel.harsh'
    _description = 'Harsh'
    _inherit = "sale.order"

    def harsh_report(self):
        return {
            'name': 'Harsh report',
            'type': 'ir.actions.act_window',
            'res_model': 'travel.print_report',
            'view_mode': 'form',
            'view_id': self.env.ref('Tourism.view_print_report_wizard_form').id,
            'target': 'new',
        }
