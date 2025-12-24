from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pos_bg_color = fields.Char(
        string='POS Tile Background Color',
        help='CSS color (e.g. #ff0000, yellow, rgb(255,0,0))',
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    pos_bg_color = fields.Char(
        related='product_tmpl_id.pos_bg_color',
        store=True,
        readonly=False,
    )
