# models/invoicelog.py
from odoo import models, fields, api

class PosInvoiceLog(models.Model):
    _name = "pos.invoice.log" 
    _description = "POS Invoice Log"

    # Core
    name = fields.Char(string="Reference", required=True)
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id.id,
        required=True,
    )

    # Parties / context
    partner_id = fields.Many2one("res.partner", string="Customer", index=True)
    pos_order_id = fields.Many2one("pos.order", string="POS Order", index=True)
    session_id = fields.Many2one("pos.session", string="Session", index=True)
    user_id = fields.Many2one("res.users", string="Cashier")

    # Lines
    line_ids = fields.One2many("pos.invoice.log.line", "log_id", string="Lines")

    # Totals (computed live from lines)
    amount_untaxed = fields.Monetary(
        string="Untaxed",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
        readonly=True,
    )
    amount_tax = fields.Monetary(
        string="Tax",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
        readonly=True,
    )
    amount_total = fields.Monetary(
        string="Total",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True,
        readonly=True,
    )

    @api.depends(
        "line_ids.subtotal",
        "line_ids.subtotal_incl",
    )
    def _compute_amounts(self):
        """Sum line subtotals whenever a line changes."""
        for log in self:
            untaxed = 0.0
            incl = 0.0
            for line in log.line_ids:
                untaxed += line.subtotal or 0.0
                incl += line.subtotal_incl or 0.0
            # Round using currency (if set)
            currency = log.currency_id or self.env.company.currency_id
            if currency:
                untaxed = currency.round(untaxed)
                incl = currency.round(incl)
            log.amount_untaxed = untaxed
            log.amount_tax = incl - untaxed
            log.amount_total = incl  # = untaxed + tax
