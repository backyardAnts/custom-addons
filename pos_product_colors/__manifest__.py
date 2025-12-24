{
    'name': 'POS Product Colors',
    'version': '16.0.1.0.0',
    'summary': 'Background colors for POS product tiles',
    'category': 'Point of Sale',
    'author': 'Diclan',
    'license': 'LGPL-3',
    'depends': [
        'product',
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_view.xml',
    ],
    'assets': {
    'point_of_sale.assets': [
        'pos_product_colors/static/src/xml/pos_product_tile_color.xml',
        'pos_product_colors/static/src/scss/pos_product_fonts.scss',
        'pos_product_colors/static/src/css/pos_hide_price.css',
        'pos_product_colors/static/src/css/pos_product_center_text.css',
    ],
},


    'installable': True,
    'application': False,
}
