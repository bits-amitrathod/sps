# -*- coding: utf-8 -*-
import werkzeug
from collections import OrderedDict
from odoo import fields as odoo_fields, tools, _
from odoo import exceptions, http, _
from odoo.http import request
from odoo.tools import consteq
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.osv import expression
from odoo.exceptions import AccessError
from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager, CustomerPortal

class WebsiteSale(http.Controller):

    def _order_check_access(self, order_id, access_token=None):
        order = request.env['sale.order'].browse([order_id])
        order_sudo = order.sudo()
        try:
            order.check_access_rights('read')
            order.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(order_sudo.access_token, access_token):
                raise
        return order_sudo

    def _order_get_page_view_values(self, order, access_token, **kwargs):
        order_invoice_lines = {il.product_id.id: il.invoice_id for il in order.invoice_ids.mapped('invoice_line_ids')}
        values = {
            'order': order,
            'order_invoice_lines': order_invoice_lines,
        }
        if access_token:
            values['no_breadcrumbs'] = True
            values['access_token'] = access_token
        values['portal_confirmation'] = order.get_portal_confirmation_action()

        if kwargs.get('error'):
            values['error'] = kwargs['error']
        if kwargs.get('warning'):
            values['warning'] = kwargs['warning']
        if kwargs.get('success'):
            values['success'] = kwargs['success']

        history = request.session.get('my_orders_history', [])
        values.update(get_records_pager(history, order))

        return values


    @http.route(['/shop/engine/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def update_engine_json(self, quote_id,product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        count = request.website.sale_get_engine_order(quote_id, line_id, set_qty,product_id)
        return count

    @http.route(['/shop/engine/count'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, quote_id,product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        count = request.website.sale_get_engine_count(quote_id,product_id)
        return count

    @http.route(['/my/orders/edit/<int:order>'], type='http', auth="public", website=True)
    def portal_order_page(self, order=None, access_token=None, **kw):
        try:
            order_sudo = self._order_check_access(order, access_token=access_token)
        except AccessError as e:
            print(e)
            return request.redirect('/my')
        values = self._order_get_page_view_values(order_sudo, access_token, **kw)
        return request.render("website_quote_ext.portal_order_page_ex", values)


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        # get customer sales rep
        sales_user = False
        partner = request.env.user.partner_id
        if partner.user_id and not partner.user_id._is_public():
            sales_user = partner.user_id

        return {
            'sales_user': sales_user,
            'page_name': 'home',
            'archive_groups': [],
        }

    def _get_archive_groups(self, model, domain=None, fields=None, groupby="create_date", order="create_date desc"):
        if not model:
            return []
        if domain is None:
            domain = []
        if fields is None:
            fields = ['name', 'create_date']
        groups = []
        for group in request.env[model]._read_group_raw(domain, fields=fields, groupby=groupby, orderby=order):
            dates, label = group[groupby]
            date_begin, date_end = dates.split('/')
            groups.append({
                'date_begin': odoo_fields.Date.to_string(odoo_fields.Date.from_string(date_begin)),
                'date_end': odoo_fields.Date.to_string(odoo_fields.Date.from_string(date_end)),
                'name': label,
                'item_count': group[groupby + '_count']
            })
        return groups

    @http.route(['/my/vendor', '/my/vendor/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_vendor_offer(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        PurchaseOrder = request.env['purchase.order']

        domain = [
            '|',
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
        ]

        archive_groups = self._get_archive_groups('purchase.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
            'amount_total': {'label': _('Total'), 'order': 'amount_total desc, id desc'},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', 'in', ['purchase', 'done', 'cancel'])]},
            'vendor offer': {'label': _('Vendor Offer'), 'domain': [('state', '=', 'ven_draft')]},
            'cancel': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},
            'done': {'label': _('Locked'), 'domain': [('state', '=', 'done')]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        vendor_count = PurchaseOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/vendor",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=vendor_count,
            page=page,
            step=self._items_per_page
        )
        # search the purchase orders to display, according to the pager data
        orders = PurchaseOrder.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_purchases_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders,
            'page_name': 'Vendor Offer',
            'pager': pager,
            'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/vendor',
        })
        return request.render("website_quote_ext.portal_my_vendor_offers", values)
