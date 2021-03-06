# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def sale_get_engine_order(self, order_id,line_id,set_qty,product_id):

        order = self.env['sale.order'].search([('id', '=', order_id)])[0]
        values = {'product_uom_qty':set_qty}
        line = self.env['sale.order.line'].sudo().search([('id', '=', line_id)])[0]
        line.write(values)
        customer = self.env['res.partner'].sudo().search([('id', '=', order.partner_id.id)])[0]
        cust_id = order.partner_id.id
        if customer.is_parent is False:
            cust_id = customer.parent_id
        count = self.env['prioritization.engine.model'].get_available_product_count(cust_id, product_id)
        return count;

    @api.multi
    def sale_get_engine_count(self, order_id,product_id):
        order = self.env['sale.order'].search([('id', '=', order_id)])[0]
        customer = self.env['res.partner'].sudo().search([('id', '=', order.partner_id.id)])[0]
        cust_id = order.partner_id.id
        if customer.is_parent is False:
            cust_id = customer.parent_id
        count = self.env['prioritization.engine.model'].get_available_product_count(cust_id, product_id)
        return count;

    @api.multi
    def sale_order_line_del(self, order_id,line_id, product_id):
        line = self.env['sale.order.line'].search([('id', '=', line_id)])[0]
        line.unlink()
        '''customer = self.env['res.partner'].sudo().search([('id', '=', order.partner_id.id)])[0]
        cust_id = order.partner_id.id
        if customer.is_parent is False:
            cust_id = customer.parent_id
        count = self.env['prioritization.engine.model'].get_available_product_count(cust_id, product_id)
        return count;'''

