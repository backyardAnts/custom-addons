from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"

    # Rename the helper M2O to avoid label clash; it's just for our linkage
    customer_invoice_id = fields.Many2one(
        "account.move", string="Customer Invoice", readonly=True, copy=False
    )

    def _create_customer_invoice(self):
        """Create & post a Customer Invoice (account.move) from this POS order."""
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Please set a customer on POS order %s before payment.") % self.name)

        journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.company_id.id)], limit=1
        )
        if not journal:
            raise UserError(_("No Sales journal found for %s.") % self.company_id.display_name)

        move_vals = {
            "move_type": "out_invoice",
            "partner_id": self.partner_id.id,
            "invoice_origin": self.name,
            "invoice_date": fields.Date.context_today(self),
            "journal_id": journal.id,
            "invoice_line_ids": [],
        }

        line_vals_list = []
        for l in self.lines:
            product = l.product_id.with_company(self.company_id)
            accounts = product._get_product_accounts()
            income_account = accounts.get("income")
            taxes = l.tax_ids_after_fiscal_position

            vals = {
                "name": product.display_name,
                "product_id": product.id,
                "quantity": l.qty,
                "price_unit": l.price_unit,
                "discount": l.discount or 0.0,
                "tax_ids": [(6, 0, taxes.ids)],
            }
            if income_account:
                vals["account_id"] = income_account.id
            line_vals_list.append((0, 0, vals))

        if not line_vals_list:
            raise UserError(_("POS order %s has no lines to invoice.") % self.name)

        move_vals["invoice_line_ids"] = line_vals_list
        move = self.env["account.move"].create(move_vals)
        move.action_post()
        return move

   # ... keep your imports and class from before ...

    def write(self, vals):
        previously_paid = {rec.id: rec.state in ("paid", "invoiced", "done") for rec in self}
        res = super().write(vals)

        if "state" in vals:
            for rec in self:
                now_paid = rec.state in ("paid", "invoiced", "done")
                became_paid = now_paid and not previously_paid.get(rec.id)

                if became_paid:
                    try:
                        move = rec.customer_invoice_id
                        if not move and rec.partner_id:
                            move = rec._create_customer_invoice()
                            rec.customer_invoice_id = move.id

                        # Prepare line commands
                        line_cmds = []
                        for l in rec.lines:
                            tax_names = ", ".join(l.tax_ids_after_fiscal_position.mapped("name"))
                            line_cmds.append((0, 0, {
                                "product_id": l.product_id.id,
                                "qty": l.qty,
                                "price_unit": l.price_unit,
                                "discount": l.discount or 0.0,
                                "taxes": tax_names,
                                "subtotal": l.price_subtotal,
                                "subtotal_incl": l.price_subtotal_incl,
                            }))

                        # Create the log with lines + context info
                        self.env["pos.invoice.log"].sudo().create({
                            "name": rec.name,
                            "partner_id": rec.partner_id.id or False,
                            "pos_order_id": rec.id,
                            "session_id": rec.session_id.id or False,
                            "user_id": rec.user_id.id or False,
                            "amount_total": rec.amount_total,
                            "currency_id": (
                                rec.pricelist_id.currency_id.id
                                if rec.pricelist_id else self.env.company.currency_id.id
                            ),
                            "line_ids": line_cmds,
                        })
                    except Exception:
                        _logger.exception("Creating invoice/log failed for POS order %s", rec.name)

        return res
