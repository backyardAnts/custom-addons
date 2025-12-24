# pos_invoice_diclan/report/sales_report_handler.py
from odoo import api, models

class ReportDiclanPosLogs(models.AbstractModel):
    _name = "report.pos_invoice_diclan.sales_logs_pdf_document"
    _description = "Diclan POS Sales Report (handler)"

    @api.model
    def _get_report_values(self, docids, data=None):
        # data is what you passed from the wizard via report_action(..., data=...)
        payload = data or {}
        return {
            "doc_ids": docids,
            "doc_model": "pos.sales.report.wizard",
            "docs": payload,  # <- expose payload as `docs` for the template
        }
