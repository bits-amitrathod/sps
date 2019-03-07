# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from odoo import api, models
import logging

_logger = logging.getLogger(__name__)
class ReportSaleOrderLineGroupByProduct(models.AbstractModel):
    _name = 'report.report_sale_orders_groupby_product.group_by_product'

    @api.model
    def get_report_values(self, docids, data=None):

        sale_order_lines =self.env['sale.order.line'].browse(docids)
        _logger.info("sale line: %r",sale_order_lines)
        self.env.cr.execute("""
                   SELECT 
                      distinct sale_order_line.product_id,
                      product_template.name,
                      array_agg(ARRAY[
                             sale_order.name,
                            to_char(sale_order.date_order,'MM/DD/YYYY'),
                            product_template.sku_code,
                            CAST (concat(cast(round(stock_move.product_uom_qty) as text),'  ',product_uom.name) as text),
                            CAST (sale_order_line.price_subtotal as text),
                            CAST (sale_order_line.currency_id as text)
                        ]) as table
                    FROM 
                      public.sale_order_line 
                      left join public.stock_move on public.stock_move.sale_line_id=sale_order_line.id,
                      public.sale_order, 
                      public.product_product, 
                      public.product_template left join  public.product_uom on  public.product_uom.id= product_template.uom_id 
                    WHERE 
                      sale_order_line.product_id = product_product.id AND
                      sale_order.id = sale_order_line.order_id AND
                      product_product.product_tmpl_id = product_template.id and sale_order_line.id in (""" + ",".join(
            map(str, docids)) + """)
                    Group BY
                      product_template.name,sale_order_line.product_id
                    Order BY
                      product_template.name desc
                  """)

        result = self.env.cr.dictfetchall()


        popup = self.env['popup.sale.orders.groupby.product.report'].search([('create_uid', '=', self._uid)], limit=1,
                                                                            order="id desc")


        return {
            'data': result,
            'popup': popup
        }
