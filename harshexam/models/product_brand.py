from odoo import fields, models, api, exceptions


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'

    name = fields.Char(string="Name")
    is_published = fields.Boolean(string="Published")
    product_ids = fields.One2many(comodel_name="product.template",inverse_name="brand_id", string="Products")
    image = fields.Image(string="Image")


    def unlink(self):
        for record in self:
            raise exceptions.UserError("Deletion of records is not allowed for this model.")
        return super(ProductBrand, self).unlink()


