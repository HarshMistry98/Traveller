from odoo import fields, models, api


class ModelName(models.Model):
    _name = 'travel.demo'
    _description = 'Description'
    _inherits = {"travel.reservation_booking":"booking_id"}

    name = fields.Char()

    @api.depends('itinerary_id', 'discount_id')
    def _compute_it_amount(self):
        for record in self:
            if record.itinerary_id and record.discount_id:
                price = record.itinerary_id.price
                discount_percentage = record.discount_id.discount_percentage
                discounted_price = price - (price * discount_percentage / 100)
                record.it_amount = discounted_price
            else:
                record.it_amount = record.itinerary_id.price

    @api.onchange('flight_tp_amount', "it_amount")
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.it_amount + record.flight_tp_amount

    def action_view_invoice(self):
        invoice_action = self.env.ref('Tourism.action_travel_reservation_invoice').read()[0]
        invoice_action.update({
            'domain': [('customer_id', '=', self.id)],
        })
        return invoice_action

    def action_select_transportation(self):
        return {
            'name': 'Transportation Selection',
            'type': 'ir.actions.act_window',
            'res_model': 'travel.transportation.selection',
            'view_mode': 'form',
            'view_id': self.env.ref('Tourism.view_transportation_selection_form').id,
            'target': 'new',
        }


