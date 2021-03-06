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
import logging
from odoo import api, fields, models
from odoo.tools import float_repr
import datetime

log = logging.getLogger(__name__)

class ReportProductVendorList(models.AbstractModel):
    _name = 'report.product_vendor_list.productvendorlist_temp_test'
    @api.model
    def get_report_values(self, docids, data=None):
         return {'data': list(self.env['purchase.order.line'].browse(docids))}