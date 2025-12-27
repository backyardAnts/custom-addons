from odoo import models, fields, api


class PosInvoiceLogLine(models.Model):
    _name = "pos.invoice.log.line"
    _description = "POS Invoice Log Line"

    log_id = fields.Many2one(
        "pos.invoice.log",
        string="Log",
        required=True,
        ondelete="cascade",
        index=True,
    )

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
        index=True,
    )

    qty = fields.Float(string="Qty", default=1.0)

    price_unit = fields.Monetary(
        string="Unit Price",
        currency_field="currency_id",
        required=True,
    )

    discount = fields.Float(string="Discount (%)", default=0.0)

    # ✅ REAL TAXES (not Char)
    tax_ids = fields.Many2many(
        "account.tax",
        string="Taxes",
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="log_id.currency_id",
        store=True,
        readonly=True,
    )

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

    # ---------------------------------------------------------
    # COMPUTATION (THIS IS THE FIX)
    # ---------------------------------------------------------

    @api.depends("qty", "price_unit", "discount", "tax_ids")
    def _compute_line_amounts(self):
        for line in self:
            qty = max(line.qty or 0.0, 0.0)

            disc = min(max(line.discount or 0.0, 0.0), 100.0)
            price_eff = (line.price_unit or 0.0) * (1.0 - disc / 100.0)

            currency = (
                line.currency_id
                or line.log_id.currency_id
                or line.env.company.currency_id
            )

            # Base price before tax engine
            base_price = price_eff * qty

            # 🔑 LET ODOO HANDLE TAX (incl / excl automatically)
            taxes_res = line.tax_ids.compute_all(
                base_price,
                currency=currency,
                quantity=1.0,
                product=line.product_id,
                partner=line.log_id.partner_id,
            )

            line.subtotal = currency.round(taxes_res["total_excluded"])
            line.subtotal_incl = currency.round(taxes_res["total_included"])
