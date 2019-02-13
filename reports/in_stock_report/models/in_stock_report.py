from odoo import  tools
import logging
from odoo.addons import decimal_precision as dp
import datetime

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ReportInStockReportPopup(models.TransientModel):
    _name = 'popup.report.in.stock.report'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    partner_id = fields.Many2one('res.partner', string='Customer', )
    user_id = fields.Many2one('res.users', 'Salesperson')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    sku_code = fields.Char('Product SKU')

    def open_table(self):
        tree_view_id = self.env.ref('in_stock_report.view_in_stock_report_line_tree').id
        margins_context = {'start_date': self.start_date,'end_date':self.end_date}
        res_model = 'report.in.stock.report'
        self.env[res_model].with_context(margins_context).delete_and_create()


        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'name': 'In Stock Report',
            'res_model': res_model,
            'context':margins_context,
            'domain': [('qty_available','>',0)]
        }

        if self.partner_id.id:
            action["domain"].append(('partner_id', '=', self.partner_id.id))

        if self.user_id.id:
            action["domain"].append(('user_id', '=', self.user_id.id))

        if self.warehouse_id.id:
            action["domain"].append(('warehouse_id', '=', self.warehouse_id.id))

        if self.sku_code:
            action["domain"].append(('sku_code', 'ilike', self.sku_code))



        return action


class ReportInStockReport(models.Model):
    _name = 'report.in.stock.report'
    _auto = False

    _inherits = {'product.template': 'product_tmpl_id'}


    partner_id = fields.Many2one('res.partner', string='Customer', )
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    product_brand_id = fields.Many2one(
        'product.brand',
        string='Manufacture',
        help='Select a Manufacture for this product'
    )
    product_id = fields.Many2one('product.product', string='Product', )
    product_tmpl_id = fields.Many2one('product.template', 'Product Template')

    min_expiration_date = fields.Date("Min Expiration Date", compute='_calculate_max_min_lot_expiration')
    max_expiration_date = fields.Date("Max Expiration Date", store=False)
    price_list=fields.Float("Sales Price",compute='_calculate_max_min_lot_expiration')
    confirmation_date = fields.Date('Confirmation Date',)
    partn_name=fields.Char()

    @api.multi
    def _calculate_max_min_lot_expiration(self):
        for record in self:
            record.price_list = record.partner_id.property_product_pricelist.get_product_price(record.product_id, 1.0, record.partner_id)
            self.env.cr.execute(
                "SELECT min(use_date), max (use_date) FROM stock_production_lot where product_id = %s",
                (record.product_id.id,))
            query_result = self.env.cr.dictfetchone()
            record.min_expiration_date = fields.Date.from_string(query_result['min'])
            record.max_expiration_date = fields.Date.from_string(query_result['max'])

    @api.model_cr
    def init(self):
        self.init_table()

    def init_table(self):
        tools.drop_view_if_exists(self._cr, self._name.replace(".", "_"))
        s_date = self.env.context.get('start_date')
        e_date = self.env.context.get('end_date')

        sql_query = """
            SELECT DISTINCT 
             ON(CONCAT(sale_order.partner_id, product_product.id)) CONCAT(sale_order.partner_id, product_product.id) as partn_name,
            sale_order_line.id as id,
            sale_order.partner_id,
            sale_order.user_id,
            sale_order.confirmation_date,
            product_template.product_brand_id,
            product_product.id AS product_id,
            product_template.id AS product_tmpl_id,
            sale_order.warehouse_id,
            null as min_expiration_date,
            null as max_expiration_date
            FROM
            sale_order
            INNER JOIN
            sale_order_line
            ON(
            sale_order.id = sale_order_line.order_id)
            INNER JOIN
            product_product
            ON
            (
            sale_order_line.product_id = product_product.id)
            INNER JOIN
            product_template
            ON
            (
            product_product.product_tmpl_id = product_template.id)
            """
        if s_date and e_date and not s_date is None and not e_date is None:
            e_date = datetime.datetime.strptime(str(e_date), "%Y-%m-%d")
            e_date = e_date + datetime.timedelta(days=1)
            sql_query=sql_query+""" and sale_order.state in ('sale','sent') and sale_order.date_order>=%s  and sale_order.date_order<=%s"""
            sql_query = "CREATE VIEW " + self._name.replace(".", "_") + " AS ( " + sql_query + " )"
            self._cr.execute(sql_query, (str(s_date), str(e_date)))
        else:
            sql_query = "CREATE VIEW " + self._name.replace(".", "_") + " AS ( " + sql_query + " )"
            self._cr.execute(sql_query)

    @api.model_cr
    def delete_and_create(self):
        self.init_table()


class ReportPrintInStockReport(models.AbstractModel):
    _name = 'report.in_stock_report.in_stock_report_print'

    @api.model
    def get_report_values(self, docids, data=None):
        dates_picked = self.env['popup.report.in.stock.report'].search([('create_uid', '=', self._uid)], limit=1,
                                                                  order="id desc")

        # if dates_picked.start_date and dates_picked.end_date and  not dates_picked.start_date is None and not dates_picked.end_date is None:
        #     date_range = (str(dates_picked.start_date)).replace("-", "/") + " - " + (str(dates_picked.end_date)).replace("-", "/")
        # else:
        #     date_range = False
        return {'dateRange':dates_picked ,'data': self.env['report.in.stock.report'].browse(docids)}
