from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        """Add pos_bg_color to products loaded into POS"""
        params = super()._loader_params_product_product()
        params["search_params"]["fields"].append("pos_bg_color")
        return params
