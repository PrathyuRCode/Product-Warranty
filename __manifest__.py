{
    'name': 'Product Warranty',
    'version': '16.0.1.0.0',
    'summary': 'Products Warranty',
    'sequence': -2,
    'installable': True,
    'application': True,

    'depends': ['base', 'account', 'stock', 'sale'],
    'data': [
        'security/warranty_security.xml',
        'security/ir.model.access.csv',
        'data/warranty_location.xml',
        'view/product_warranty_views.xml',
        'view/product_views.xml',
        'view/invoice_views.xml',
        'report/product_warranty_report.xml',
        'wizard/wizard_report_views.xml',
        'view/product_warranty_menus.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'product_warranty/static/src/js/action_manager.js'
        ]
    },

}
