{
    'name': 'POS Invoice Diclan',
    'version': '17.0.1.0.0',
    'summary': 'Scaffold for POS invoicing project',
    'category': 'Point of Sale',
    'author': 'Diclan',
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_invoice_log_views.xml',
        'views/sales_report_wizard_views.xml',
        'reports/sales_report_templates.xml',
        'reports/sales_report_action.xml',
        'views/menuitems.xml',
    ],
    'application': True,
    'installable': True,
}
