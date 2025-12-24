# models/log_line.py
from odoo import models, fields, api

class PosInvoiceLogLine(models.Model):
    _name = "pos.invoice.log.line"
    _description = "POS Invoice Log Line"

    log_id = fields.Many2one(
        "pos.invoice.log", string="Log", required=True, ondelete="cascade", index=True
    )
    product_id = fields.Many2one("product.product", string="Product", required=True, index=True)

    qty = fields.Float(string="Qty", default=1.0)
    price_unit = fields.Monetary(string="Unit Price")
    discount = fields.Float(string="Discount (%)", default=0.0)
    taxes = fields.Char(string="Taxes")  # display-only for now

    subtotal = fields.Monetary(
        string="Subtotal (excl)",
        currency_field="currency_id",
        compute="_compute_line_amounts",
        store=True,
        readonly=True,
    )
    subtotal_incl = fields.Monetary(
        string="Subtotal (incl)",
        currency_field="currency_id",
        compute="_compute_line_amounts",
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency", related="log_id.currency_id", store=True, readonly=True
    )

    # --- Computations ---

    @api.depends("qty", "price_unit", "discount")
    def _compute_line_amounts(self):
        """Compute subtotal and subtotal_incl from qty/price/discount.
        For now, taxes are display-only; subtotal_incl == subtotal.
        """
        for line in self:
            qty = max(line.qty or 0.0, 0.0)  # clamp to >= 0
            disc = line.discount or 0.0
            if disc < 0.0:
                disc = 0.0
            if disc > 100.0:
                disc = 100.0
            price_eff = (line.price_unit or 0.0) * (1.0 - (disc / 100.0))
            subtotal = qty * price_eff
            # Round using currency if present
            currency = line.currency_id or line.log_id.currency_id or line.env.company.currency_id
            if currency:
                subtotal = currency.round(subtotal)
            line.subtotal = subtotal
            line.subtotal_incl = subtotal  # no tax math yet

    # --- Onchanges for instant UI updates (before save) ---

    @api.onchange("qty", "price_unit", "discount")
    def _onchange_recompute_amounts(self):
        """Ensure live UI feedback when editing in the form (editable tree)."""
        for line in self:
            # Normalize values for better UX
            if line.qty is not None and line.qty < 0:
                line.qty = 0.0
            if line.discount is not None:
                if line.discount < 0.0:
                    line.discount = 0.0
                elif line.discount > 100.0:
                    line.discount = 100.0
            # Reuse compute logic for UI refresh
            line._compute_line_amounts()

    @api.onchange("product_id")
    def _onchange_product_defaults(self):
        """Optional: set default price/taxes text when product changes."""
        for line in self:
            if not line.product_id:
                continue
            # Pull standard price as a simple default. Replace with pricelist logic if desired.
            line.price_unit = line.product_id.lst_price or 0.0
            # Display-only taxes text (join names). This mirrors how you created the log.
            taxes = line.product_id.taxes_id
            line.taxes = ", ".join(taxes.mapped("name")) if taxes else False
            # Reset discount for safety
            if line.discount is None:
                line.discount = 0.0
            # Trigger recompute for the new product defaults
            line._compute_line_amounts()
