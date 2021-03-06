# -*- coding: utf-8 -*-
{

    'name': "Sales By Count",
    'summary':"Report",
    'author': "Benchmark IT Solutions",
    'website': "http://www.benchmarkitsolutions.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','prioritization_engine'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'report/sales_by_count_report.xml',
        'report/sales_by_count_report_template.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}
