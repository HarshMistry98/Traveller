from odoo import models


class InvoiceXlsx(models.AbstractModel):
    _name = "report.Tourism.invoice_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Invoice XLSX Report"

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet("Report")
        for i, obj in enumerate(partners):
            bold = workbook.add_format({"bold": True})
            sheet.write(i, 0, obj.invoice_seq, bold)
            sheet.write(i, 1, obj.customer_id.first_name, bold)
            sheet.write(i, 2, obj.itinerary_id.itinerary_name, bold)
            sheet.write(i, 3, obj.agency_id.agency_name, bold)
            sheet.write(i, 4, obj.discount_id.discount_percentage, bold)
            sheet.write(i, 5, obj.booking_id.booking_seq, bold)
            sheet.write(i, 6, obj.payment_id.payment_seq, bold)
            sheet.write(i, 7, obj.it_amount, bold)
            sheet.write(i, 8, obj.transport_id.transport_seq, bold)
            sheet.write(i, 9, obj.tp_amount, bold)
            sheet.write(i, 10, obj.due_date, bold)
            sheet.write(i, 11, obj.total_amount, bold)
            sheet.write(i, 12, obj.status, bold)