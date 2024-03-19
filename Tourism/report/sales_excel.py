from odoo import models

class InvoiceXlsx(models.AbstractModel):
    _name = "report.Tourism.sales_excel_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Sales XLSX Report"

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet("Report")
        for i, obj in enumerate(partners):
            bold = workbook.add_format({"bold": True})
            sheet.write(i, 0, obj.name, bold)
            sheet.write(i, 1, obj.date_order, bold)
            sheet.write(i, 2, obj.website_id, bold)
            sheet.write(i, 3, obj.partner_id, bold)
            sheet.write(i, 4, obj.company_id, bold)
            sheet.write(i, 5, obj.amount_total, bold)
            sheet.write(i, 6, obj.invoice_status, bold)
