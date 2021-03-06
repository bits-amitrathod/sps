from odoo import api, fields, models,_
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat, misc

class SaleSalespersonReport(models.TransientModel):
    _name = 'sale.purchase.history.report'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    product_id = fields.Many2many('product.product', string="Products")
    order_partner_id = fields.Many2one('res.partner', string='Customer')

    @api.multi
    def open_table(self):
        tree_view_id = self.env.ref('sales_purchase_history_report.list_view').id
        form_view_id = self.env.ref('sales_purchase_history_report.view_sales_order_line_view_cstm').id
        if self.start_date and self.end_date:
            e_date = SaleSalespersonReport.string_to_date(str(self.end_date))
            e_date = e_date + datetime.timedelta(days=1)
            s_date=SaleSalespersonReport.string_to_date(str(self.start_date))

            sale_order_line=self.env['sale.order.line'].search([('create_date', '>=', str(s_date)), ('create_date', '<=', str(e_date)), ('state', 'not in', ('cancel','void')),]).ids
        else:
            sale_order_line = self.env['sale.order.line'].search([('state', 'not in', ('cancel', 'void')), ]).ids
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'name': _('Sales Purchase History'),
            'res_model': 'sale.order.line',
            'domain': [ ('id', 'in', sale_order_line),('qty_delivered','>',0),('price_unit','>=',0)],
            'target': 'main'
        }

        if self.product_id and self.order_partner_id:
            action['domain'].append(('product_id', '=', self.product_id.id))
            action['domain'].append(('order_partner_id', '=', self.order_partner_id.id))
        elif self.product_id:
            action['domain'].append(('product_id', '=', self.product_id.id))
        elif self.order_partner_id:
            action['domain'].append(('order_partner_id', '=', self.order_partner_id.id))
        return action

    @staticmethod
    def string_to_date(date_string):
        return datetime.datetime.strptime(date_string, DEFAULT_SERVER_DATE_FORMAT).date()