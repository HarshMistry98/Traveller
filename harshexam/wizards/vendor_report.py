from odoo import fields, models, api


class VendorReport(models.TransientModel):
    _name = 'vendor.report'
    _description = 'Wizard for Vendor Report'

    partner_ids = fields.Many2many(comodel_name="res.partner", domain="[('supplier_rank', '>', 0)]")

    # @api.model
    # def default_get(self, fields):
    #     res = super(VendorReport, self).default_get(fields)
    #     print("res",res)
    #     supplier_ids = self.env["res.partner"].search([('supplier_rank', '>', 0)]).ids
    #     print("supplier_ids",supplier_ids)
    #     if supplier_ids:
    #         res['partner_ids'] = [(6, 0, supplier_ids)]
    #         print(res)
    #     return res

    def action_show_orders(self):
        print("Orders")
        supplier_ids = self.partner_ids.ids
        purchase_order_ids = self.env['purchase.order'].search([("partner_id", "in", supplier_ids)]).ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'tree',
            'domain': [('id', 'in', purchase_order_ids)],
        }
