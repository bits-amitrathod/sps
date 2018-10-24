
from odoo import api, fields, models
from lxml import etree
from datetime import datetime
import calendar
from dateutil.relativedelta import relativedelta


class TrendingReportListView(models.Model):

    _inherit = 'res.partner'

    month1 = fields.Float('month1',  store=False)
    month2 = fields.Float('month2', store=False)
    month3 = fields.Float('month3', store=False)
    month4 = fields.Float('month4', store=False)
    month5 = fields.Float('month5', store=False)
    month6 = fields.Float('month6', store=False,compute='_compute_sales_vals')
    trend_val = fields.Char('Trend', store=False,compute='_get_trend_value')
    average_sale = fields.Float('Average', store=False,compute='_get_average_value')
    total_sale = fields.Float('Total', store=False,compute='_get_total_value')

    #@api.onchange('month6')
    def _compute_sales_vals(self):
        for product in self:
            groupby_dict = groupby_dict_month = groupby_dict_90 = groupby_dict_yr = {}
            sale_orders = self.env['sale.order'].search([('partner_id', '=', product.id), ('state', '=', 'sale')])
            groupby_dict_month['data'] = sale_orders
            for sale_order in groupby_dict_month['data']:
                confirmation_date=datetime.date(datetime.strptime(sale_order.confirmation_date,"%Y-%m-%d %H:%M:%S"))
                if((confirmation_date.month == (fields.date.today() - relativedelta(months=5)).month) and (confirmation_date.year ==  (fields.date.today() - relativedelta(months=5)).year)):
                    product.month6 = product.month6 + sale_order.amount_total
                if((confirmation_date.month == (fields.date.today() - relativedelta(months=4)).month) and (confirmation_date.year ==  (fields.date.today() - relativedelta(months=4)).year)):
                    product.month5 = product.month5 + sale_order.amount_total
                if((confirmation_date.month == (fields.date.today() - relativedelta(months=3)).month) and (confirmation_date.year ==  (fields.date.today() - relativedelta(months=3)).year)):
                    product.month4 = product.month4 + sale_order.amount_total
                if((confirmation_date.month == (fields.date.today() - relativedelta(months=2)).month) and (confirmation_date.year ==  (fields.date.today() - relativedelta(months=2)).year)):
                    product.month3 = product.month3 + sale_order.amount_total
                if((confirmation_date.month == (fields.date.today() - relativedelta(months=1)).month) and (confirmation_date.year ==  (fields.date.today() - relativedelta(months=1)).year)):
                    product.month2 = product.month2 + sale_order.amount_total
                if((confirmation_date.month == (fields.date.today()).month) and (confirmation_date.year ==  (fields.date.today()).year)):
                    product.month1 = product.month1 + sale_order.amount_total

    @api.onchange('trend_val')
    def _get_total_value(self):
        for customer in self:
            customer.total_sale=customer.month1+customer.month2+customer.month3+customer.month4+customer.month5+customer.month6

    @api.onchange('total_sale')
    def _get_trend_value(self):
        for customer in self:
            if(customer.average_sale < customer.month1):
                customer.trend_val='UP'
            elif(customer.average_sale > customer.month1):
                customer.trend_val = 'DOWN'
            elif (customer.average_sale == customer.month1):
                customer.trend_val = 'EQUAL'
            if (customer.month1 == 0):
                customer.trend_val = 'NO SALE'


    @api.onchange('average_sale')
    def _get_average_value(self):
        for customer in self:
            count = 0
            if(customer.month1):
                count=count+1
            if(customer.month2):
                count=count+1
            if(customer.month3):
                count=count+1
            if(customer.month4):
                count=count+1
            if(customer.month5):
                count=count+1
            if(customer.month6):
                count=count+1
            if(count):
                customer.average_sale=(customer.total_sale/count)


    @api.model
    def fields_view_get(self, view_id=None, view_type='tree', toolbar=False, submenu=False):
        res = super(TrendingReportListView, self).fields_view_get(
            view_id=self.env.ref('trending_report.trending_report_list').id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])

        '''print(fields.date.today() - datetime.timedelta(days=30))
        print(fields.date.today() - datetime.timedelta(days=60))
        print(fields.date.today() - datetime.timedelta(days=90))
        print(fields.date.today() - datetime.timedelta(days=120))
        print(fields.date.today() - datetime.timedelta(days=150))
        print(fields.date.today() - datetime.timedelta(days=180))
        print("= ==================== ========")
        print(fields.date.today() - relativedelta(months=1))
        print(fields.date.today() - relativedelta(months=2))
        print(fields.date.today() - relativedelta(months=3))
        print(fields.date.today() - relativedelta(months=4))
        print(fields.date.today() - relativedelta(months=5))
        print(fields.date.today() - relativedelta(months=6))
        print("= ====================A========")
        print((fields.date.today() - relativedelta(months=1)).strftime('%b-%Y'))

        temp_month1="Jan 17"
        temp_month2="Dec 17"
        temp_month3="Nov 17"
        temp_month4="Oct 17"
        temp_month5="Sept 17"
        temp_month6="Aug 17"'''

        for node in doc.xpath("//field[@name='month1']"):
            node.set('string', (fields.date.today()).strftime('%b-%Y'))
        for node in doc.xpath("//field[@name='month2']"):
            node.set('string', (fields.date.today() - relativedelta(months=1)).strftime('%b-%Y'))
        for node in doc.xpath("//field[@name='month3']"):
            node.set('string', (fields.date.today() - relativedelta(months=2)).strftime('%b-%Y'))
        for node in doc.xpath("//field[@name='month4']"):
            node.set('string', (fields.date.today() - relativedelta(months=3)).strftime('%b-%Y'))
        for node in doc.xpath("//field[@name='month5']"):
            node.set('string', (fields.date.today() - relativedelta(months=4)).strftime('%b-%Y'))
        for node in doc.xpath("//field[@name='month6']"):
            node.set('string', (fields.date.today() - relativedelta(months=5)).strftime('%b-%Y'))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res