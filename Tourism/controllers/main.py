import json

from odoo import http
from odoo.http import request


class Itinerary(http.Controller):

    @http.route('/itinerary', type="http", auth="public", website=True, method=['GET','POST'],
                csrf=False)
    def itinerary_controller(self):
        values = {}
        return request.render("Tourism.itinerary_menu_template", values)


