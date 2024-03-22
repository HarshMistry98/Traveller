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

    # def download(self):
    #     report = self.env.ref("Tourism.reservation_invoice_template")
    #     return report.report_action(self)

    def _get_hotel_searchbar_sortings(self):
        return {
            'date': {'label': _('Create Date'), 'order': 'create_date desc'},
        }

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        HotelBookingENV = request.env['travel.reservation_invoice'].sudo()
        if 'booking_count' in counters:
            values['booking_count'] = HotelBookingENV.search_count([])
        return values

    def _prepare_travel_portal_rendering_values(
            self, page=1, date_begin=None, date_end=None, sortby=None, quotation_page=False, **kwargs
    ):
        TravelBooking = request.env['travel.reservation_invoice']

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
        booking_ids = TravelBooking.search([], order=sort_order, limit=self._items_per_page,
                                           offset=pager_values['offset'])

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

    # def _prepare_sale_portal_rendering_values(
    #         self, page=1, date_begin=None, date_end=None, sortby=None, quotation_page=False, **kwargs):
    #
    #     TravelBooking = request.env['travel.reservation_invoice']
    #
    #     if not sortby:
    #         sortby = 'date'
    #
    #     url = "/my/invoice"

    @http.route(['/my/travels/<int:invoice_id>'], type='http', auth="user",
                website=True)

    def portal_my_travel_booking_view(self, invoice_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('travel.reservation_invoice', invoice_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type, report_ref='Tourism.reservation_invoice_template', download=download)

        # if request.env.user.share and access_token:
        #     # If a public/portal user accesses the order with the access token
        #     # Log a note on the chatter.
        #     today = fields.Date.today().isoformat()
        #     session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
        #     if session_obj_date != today:
        #         # store the date as a string in the session to allow serialization
        #         request.session['view_quote_%s' % order_sudo.id] = today
        #         # The "Quotation viewed by customer" log note is an information
        #         # dedicated to the salesman and shouldn't be translated in the customer/website lgg
        #         context = {'lang': order_sudo.user_id.partner_id.lang or order_sudo.company_id.partner_id.lang}
        #         msg = _('Quotation viewed by customer %s', order_sudo.partner_id.name)
        #         del context
        #         _message_post_helper(
        #             "sale.order",
        #             order_sudo.id,
        #             message=msg,
        #             token=order_sudo.access_token,
        #             message_type="notification",
        #             subtype_xmlid="mail.mt_note",
        #             partner_ids=order_sudo.user_id.sudo().partner_id.ids,
        #         )

        backend_url = f'/web#model={order_sudo._name}'\
                      f'&id={order_sudo.id}'\
                      f'&action={order_sudo._get_portal_return_action().id}'\
                      f'&view_type=form'
        values = {
            'invoic_order': order_sudo,
            'message': message,
            'report_type': 'html',
            'backend_url': backend_url, # Used to display correct company logo
        }


        # # Payment values
        # if order_sudo._has_to_be_paid():
        #     values.update(self._get_payment_values(order_sudo))
        #
        # if order_sudo.state in ('draft', 'sent', 'cancel'):
        #     history_session_key = 'my_quotations_history'
        # else:
        #     history_session_key = 'my_orders_history'

        history_session_key = 'my_orders_history'

        values = self._get_page_view_values(
            order_sudo, access_token, values, history_session_key, False)
        print(values)

        return request.render('Tourism.portal_view_bookings',values)
