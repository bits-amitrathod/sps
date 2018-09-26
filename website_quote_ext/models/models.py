# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def sale_get_engine_order(self, order_id,line_id,set_qty):
        print("Inside sale_get_engine_order")
        order=self.env['sale.order'].search([('id', '=', order_id)])[0]
        print(order)
        values={'product_uom_qty':set_qty}
        line=self.env['sale.order.line'].sudo().search([('id', '=', line_id)])[0]
        line.write(values)
        return line;
