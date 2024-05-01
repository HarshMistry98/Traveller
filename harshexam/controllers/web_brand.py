from odoo import http
from odoo.http import request


class WebBrand(http.Controller):

    @http.route('/brand', type="http", auth="public", website=True, method=['GET', 'POST'],
                csrf=False)
    def brand_controller(self):
        brands = request.env['product.brand'].search([])
        print("brands_", brands)
        values = {
            "brands": brands,
        }
        return request.render("harshexam.brand_menu_view_website", values)

    @http.route('/brand/products/<int:brandid>', type="http", auth="public", website=True, method=['GET', 'POST'],
                csrf=False)
    def brand_product(self,brandid):
        products = request.env['product.template'].search([("brand_id", "!=", False)])
        brand = request.env["product.brand"].browse(brandid)
        values = {
            "brand":brand,
            "products": products
        }
        return request.render("harshexam.brand_only_products", values)
        pass
