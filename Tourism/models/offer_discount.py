from datetime import date, timedelta

from Crypto.Util.number import inverse

from odoo import fields, models, api


class travel_offer_discount(models.Model):
    _name = 'travel.offer_discount'
    _description = 'All details regarding offers and discount will be shown here'
    _rec_name = "discount_description"

    # OfferID(PrimaryKey)

    discount_seq = fields.Char(string='Discount Sequence')


    itinerary_id = fields.Many2one(comodel_name="travel.itinerary", string="Itinerary")
    agency_id = fields.Many2one(comodel_name="travel.agency", string="Agency",domain="[('itinerary_ids', '=', itinerary_id)]")
    discount_description = fields.Char(string="Discount Description")
    discount_percentage = fields.Integer(string="Discount Percentage")
    validity_date = fields.Date(string="Validity Date")
    validity_days = fields.Integer(string="Validity Days", compute="_compute_validity_days", inverse="_inverse_validity_date")
    discount_terms_and_conditions = fields.Char(string="Terms and Conditions")

    @api.depends("validity_date")
    def _compute_validity_days(self):
        for record in self:
            if record.validity_date:
                current_date = date.today()
                validity_days = (record.validity_date - current_date).days
                if validity_days < 0:
                    validity_days = 0
            else:
                validity_days = 0

            record.validity_days = validity_days

    def _inverse_validity_date(self):
        for record in self:
            if record.validity_days:
                current_date = date.today()
                validity_date = current_date + timedelta(days=record.validity_days)
                record.validity_date = validity_date
            else:
                record.validity_date = False


    @api.model_create_multi
    def create(self, vals_list):
        records = super(travel_offer_discount, self).create(vals_list)
        for rec in records:
            seq = self.env['ir.sequence'].next_by_code('travel.offer.discount.seq')
            rec.discount_seq = seq
        return records

    def write(self, vals):
        if not self.discount_seq:
            seq = self.env['ir.sequence'].next_by_code('travel.offer.discount.seq')
            vals.update({
                'discount_seq': seq
            })
        res = super(travel_offer_discount, self).write(vals)
        return res



