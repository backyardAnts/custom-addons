from odoo import api, fields, models


class PosSalesReportCompute(models.AbstractModel):
    _name = "pos.sales.report.compute"
    _description = "Compute data for Diclan POS Sales Report (from pos.invoice.log)"

    @api.model
    def _prepare_report_from_ids(self, log_ids, date_from=None, date_to=None):
        Log = self.env["pos.invoice.log"].sudo()
        logs = Log.browse(log_ids).exists()

        rows = []
        total_untaxed = total_tax = grand = 0.0
        company_currency = self.env.company.currency_id

        for r in logs:
            currency = r.currency_id or company_currency

            untaxed = currency.round(r.amount_untaxed or 0.0)
            tax     = currency.round(r.amount_tax or 0.0)
            total   = currency.round(r.amount_total or 0.0)

            d = r.pos_order_id.date_order if r.pos_order_id else r.create_date
            date_str = fields.Datetime.to_string(d) if d else ""

            rows.append({
                "date": date_str,
                "name": r.name or "",
                "partner": r.partner_id.display_name if r.partner_id else "",
                "session": r.session_id.name if r.session_id else "",
                "cashier": r.user_id.display_name if r.user_id else "",
                "currency_id": currency.id,
                "amount_total": float(total),
                "amount_untaxed": float(untaxed),
                "amount_tax": float(tax),
            })

            total_untaxed += untaxed
            total_tax     += tax
            grand         += total

        return {
            "company": {"name": self.env.company.display_name},
            "period": {
                "date_from": fields.Datetime.to_string(date_from) if date_from else "",
                "date_to":   fields.Datetime.to_string(date_to)   if date_to   else "",
            },
            "logs": rows,
            "totals": {
                "untaxed": total_untaxed,
                "tax": total_tax,
                "total": grand,
                "count": len(rows),
            },
        }
