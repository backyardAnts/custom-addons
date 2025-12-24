# pos_invoice_diclan/models/sales_report_wizard.py
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class PosSalesReportWizard(models.TransientModel):
    _name = "pos.sales.report.wizard"
    _description = "POS Sales Report (Diclan)"

    def _default_date_from(self):
        now = fields.Datetime.now()
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    date_from = fields.Datetime(required=True, default=_default_date_from)
    date_to   = fields.Datetime(required=True, default=lambda self: fields.Datetime.now())

    # Toggle: filter on POS order date instead of log creation date
    use_order_date = fields.Boolean(string="Use POS Order Date", default=True)

    # Optional filters
    session_ids = fields.Many2many("pos.session", string="Sessions")
    user_ids    = fields.Many2many("res.users", string="Cashiers")
    partner_id  = fields.Many2one("res.partner", string="Customer")

    def _domain(self):
        """Build the EXACT domain used to fetch pos.invoice.log rows."""
        self.ensure_one()
        dom = []

        if self.use_order_date:
            dom.append(("pos_order_id", "!=", False))  # guard when using dotted field
            if self.date_from:
                dom.append(("pos_order_id.date_order", ">=", self.date_from))
            if self.date_to:
                dom.append(("pos_order_id.date_order", "<=", self.date_to))
        else:
            if self.date_from:
                dom.append(("create_date", ">=", self.date_from))
            if self.date_to:
                dom.append(("create_date", "<=", self.date_to))

        if self.session_ids:
            dom.append(("session_id", "in", self.session_ids.ids))
        if self.user_ids:
            dom.append(("user_id", "in", self.user_ids.ids))
        if self.partner_id:
            dom.append(("partner_id", "=", self.partner_id.id))

        return dom

    def action_preview(self):
        """Open a list of the rows the report will use."""
        self.ensure_one()
        dom = self._domain()
        _logger.warning("DICLAN PREVIEW DOMAIN: %s", dom)
        return {
            "type": "ir.actions.act_window",
            "name": "Matching Invoice Logs",
            "res_model": "pos.invoice.log",
            "view_mode": "tree,form",
            "domain": dom,
            "target": "current",
            "context": {"search_default_group_by_session_id": 0},
        }

    def action_print_pdf(self):
        """Generate the PDF using the EXACT same set as preview (IDs)."""
        self.ensure_one()
        dom = self._domain()
        logs = self.env["pos.invoice.log"].search(dom)

        data = self.env["pos.sales.report.compute"]._prepare_report_from_ids(
            log_ids=logs.ids,
            date_from=self.date_from,
            date_to=self.date_to,
        )

        act = self.env.ref("pos_invoice_diclan.action_report_pos_logs_diclan")
        _logger.warning("DICLAN REPORT ACTION: id=%s report_name=%s", act.id, act.report_name)

        return act.report_action(None, data=data)
