
{
    'name': ' Report Discount Summary',
    'category': 'Report',
    'version': '11.0.0.1',
    'author': 'Benchmark It Solutions',
    'depends': ['base', 'sale'],
    'data': [
        'views/discount_summary_view.xml',
        'report/discount_summary_report.xml',
        'report/discount_summary_temp.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}