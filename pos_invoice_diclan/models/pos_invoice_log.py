from odoo import models, fields, api


class PosInvoiceLog(models.Model):
    _name = "pos.invoice.log"
    _description = "POS Invoice Log"

    # Core
    name = fields.Char(
        string="Reference",
        required=True,
        default="New",
        copy=False,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    # Parties / context
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        index=True,
    )
    pos_order_id = fields.Many2one(
        "pos.order",
        string="POS Order",
        index=True,
    )
    session_id = fields.Many2one(
        "pos.session",
        string="Session",
        index=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Cashier",
        default=lambda self: self.env.user,
    )

    # Lines
    line_ids = fields.One2many(
        "pos.invoice.log.line",
        "log_id",
        string="Lines",
    )

    # Totals (computed from lines)
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
            untaxed = sum(log.line_ids.mapped("subtotal"))
            incl = sum(log.line_ids.mapped("subtotal_incl"))

            currency = log.currency_id or self.env.company.currency_id
            if currency:
                untaxed = currency.round(untaxed)
                incl = currency.round(incl)

            log.amount_untaxed = untaxed
            log.amount_tax = incl - untaxed
            log.amount_total = incl
