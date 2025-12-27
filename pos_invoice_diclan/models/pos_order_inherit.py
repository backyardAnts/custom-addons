from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    customer_invoice_id = fields.Many2one(
        "account.move",
        string="Customer Invoice",
        readonly=True,
        copy=False,
    )

    # ---------------------------------------------------------
    # CUSTOMER INVOICE CREATION
    # ---------------------------------------------------------

    def _create_customer_invoice(self):
        """Create & post a Customer Invoice (account.move) from this POS order."""
        self.ensure_one()

        if not self.partner_id:
            raise UserError(
                _("Please set a customer on POS order %s before payment.") % self.name
            )

        journal = self.env["account.journal"].search(
            [
                ("type", "=", "sale"),
                ("company_id", "=", self.company_id.id),
            ],
            limit=1,
        )
        if not journal:
            raise UserError(
                _("No Sales journal found for %s.") % self.company_id.display_name
            )

        invoice_lines = []
        for line in self.lines:
            product = line.product_id.with_company(self.company_id)
            accounts = product._get_product_accounts()
            income_account = accounts.get("income")

            taxes = line.tax_ids_after_fiscal_position

            vals = {
                "name": product.display_name,
                "product_id": product.id,
                "quantity": line.qty,
                "price_unit": line.price_unit,
                "discount": line.discount or 0.0,
                "tax_ids": [(6, 0, taxes.ids)],
            }
            if income_account:
                vals["account_id"] = income_account.id

            invoice_lines.append((0, 0, vals))

        if not invoice_lines:
            raise UserError(
                _("POS order %s has no lines to invoice.") % self.name
            )

        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.partner_id.id,
            "invoice_origin": self.name,
            "invoice_date": fields.Date.context_today(self),
            "journal_id": journal.id,
            "invoice_line_ids": invoice_lines,
        })

        move.action_post()
        return move

    # ---------------------------------------------------------
    # POS → INVOICE LOG CREATION (FIXED)
    # ---------------------------------------------------------

    def write(self, vals):
        previously_paid = {
            rec.id: rec.state in ("paid", "invoiced", "done")
            for rec in self
        }

        res = super().write(vals)

        if "state" in vals:
            for rec in self:
                now_paid = rec.state in ("paid", "invoiced", "done")
                became_paid = now_paid and not previously_paid.get(rec.id)

                if not became_paid:
                    continue

                try:
                    # Create customer invoice if needed
                    move = rec.customer_invoice_id
                    if not move and rec.partner_id:
                        move = rec._create_customer_invoice()
                        rec.customer_invoice_id = move.id

                    # -------------------------------------------------
                    # CREATE LOG LINES (THIS WAS THE BUG)
                    # -------------------------------------------------
                    line_cmds = []
                    for line in rec.lines:
                        line_cmds.append((0, 0, {
                            "product_id": line.product_id.id,
                            "qty": line.qty,
                            "price_unit": line.price_unit,
                            "discount": line.discount or 0.0,
                            # ✅ THIS IS THE KEY FIX
                            "tax_ids": [(6, 0, line.tax_ids_after_fiscal_position.ids)],
                        }))

                    # Create POS Invoice Log
                    self.env["pos.invoice.log"].sudo().create({
                        "name": rec.name,
                        "partner_id": rec.partner_id.id or False,
                        "pos_order_id": rec.id,
                        "session_id": rec.session_id.id or False,
                        "user_id": rec.user_id.id or False,
                        "currency_id": (
                            rec.pricelist_id.currency_id.id
                            if rec.pricelist_id
                            else self.env.company.currency_id.id
                        ),
                        "line_ids": line_cmds,
                    })

                except Exception:
                    _logger.exception(
                        "Creating invoice/log failed for POS order %s",
                        rec.name,
                    )

        return res
