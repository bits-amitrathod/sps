# -*- coding: utf-8 -*-
{
    'name': "Sales order invoices",
    'summary': """
      Report       
    """
    ,
    # 'description': """
    #     Sales order invoices with date filter
    # """,

    'author': "Benchmark IT Solutions",
    'website': "http://www.benchmarkitsolutions.com",
    'category': 'Report',
    'version': '0.1',


    'depends': ['base','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'report/report_sales_order_invoices.xml',
        'report/sales_order_invoices.xml'
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
