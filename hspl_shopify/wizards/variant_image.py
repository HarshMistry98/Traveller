from odoo import fields, models, api


class VariantImage(models.TransientModel):
    _name = 'product_variant.image'
    _description = 'Description'

    image_preview = fields.Image("Preview")
    selection_image = fields.Selection(
        selection=lambda self: self._get_selection(),
        string="Select an Image",
        default= lambda self: self.set_shpoify_image_id(),
        required=True,  # Make selection mandatory if needed
    )

    def _get_selection(self):
        records = self.env['product.image'].search([('product_tmpl_id', '=',  self._context.get('current_product_tmpl_id'))])
        return [(record.shopify_image_id, record.name) for record in records]

    def set_shpoify_image_id(self):
        return self._context.get('shopify_variant_image_id')

    @api.onchange("selection_image")
    def _onchange_selection_image(self):
        self.image_preview = self.env['product.image'].search([('shopify_image_id', '=', self.selection_image)], limit=1).image_1920

    def confirm_selection(self):
        product = self.env['product.product'].browse(self._context.get('current_product_id'))
        product.write({'shopify_variant_image_id': self.selection_image})

