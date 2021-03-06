
from odoo import api, models
from datetime import datetime


class ReportPurchaseSalespersonWise(models.AbstractModel):
    _name = 'report.inventory_adjustment_report.adjustment_report1'

    @api.model
    def get_report_values(self, docids, data=None):
        purchase_orders = self.env['stock.move.line'].browse(docids)

        popup = self.env['adj_popup.view.model'].search([('create_uid', '=', self._uid)], limit=1, order="id desc")

        if popup.compute_at_date:
            date = datetime.strptime(popup.start_date, '%Y-%m-%d').strftime('%m/%d/%Y') + " - " + datetime.strptime(
                popup.end_date, '%Y-%m-%d').strftime('%m/%d/%Y')
        else:
            date = False

        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'data': purchase_orders,
            'date': date
        }