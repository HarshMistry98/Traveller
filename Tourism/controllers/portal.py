import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class TravelPortal(portal.CustomerPortal):
    def _get_hotel_searchbar_sortings(self):
        return {
            'date': {'label': _('Create Date'), 'order': 'create_date desc'},
        }

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        HotelBookingENV = request.env['travel.itinerary'].sudo()
        if 'booking_count' in counters:
            values['booking_count'] = HotelBookingENV.search_count([])
        return values

    def _prepare_travel_portal_rendering_values(
        self, page=1, date_begin=None, date_end=None, sortby=None, quotation_page=False, **kwargs
    ):
        TravelBooking = request.env['travel.itinerary']

        if not sortby:
            sortby = 'date'

        # partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()
        url = "/my/bookings"

        # if quotation_page:
        #     url = "/my/quotes"
        #     domain = self._prepare_quotations_domain(partner)
        # else:
        #     url = "/my/orders"
        #     domain = self._prepare_orders_domain(partner)

        searchbar_sortings = self._get_hotel_searchbar_sortings()

        sort_order = searchbar_sortings[sortby]['order']

        pager_values = portal_pager(
            url=url,
            total=TravelBooking.search_count([]),
            page=page,
            step=self._items_per_page,
            url_args={'sortby': sortby},
        )
        booking_ids = TravelBooking.search([], order=sort_order, limit=self._items_per_page, offset=pager_values['offset'])

        values.update({
            'date': date_begin,
            'bookings': booking_ids.sudo() if quotation_page else TravelBooking,
            'page_name': 'booking',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return values

    @http.route(['/my/bookings', '/my/bookings/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_travel_booking(self, **kwargs):
        values = self._prepare_travel_portal_rendering_values(quotation_page=True, **kwargs)
        print("?>>>>>>>>", values)
        return request.render("Tourism.portal_my_bookings", values)