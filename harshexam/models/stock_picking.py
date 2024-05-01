from odoo import fields, models, api
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Stock Picking'

    total_pickings = fields.Integer(string="Total Pickings", compute="_compute_total_pickings")

    @api.depends("move_ids")
    def _compute_total_pickings(self):
        for rec in self:
            rec.total_pickings = len(rec.move_ids.ids)


    def unlink(self):
        for rec in self:
          if  len(rec.move_ids.ids)>3:
              raise UserError("Delivery Orders which have more 3 pickings cannot be deleted")
        return super(StockPicking, self).unlink()
