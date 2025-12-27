# Project Context

## Repository layout
- `pos_invoice_diclan/` Odoo 17 addon for POS invoice logging and sales reporting.
- `pos_product_colors/` Odoo 16 addon for POS product tile styling and background colors.

## pos_invoice_diclan key files
- `pos_invoice_diclan/__manifest__.py` addon metadata, data files, and dependencies.
- `pos_invoice_diclan/models/pos_order_inherit.py` hooks POS order state changes to create customer invoices and logs.
- `pos_invoice_diclan/models/pos_invoice_log.py` + `pos_invoice_diclan/models/pos_invoice_log_line.py` log data model and computed totals.
- `pos_invoice_diclan/models/sales_report_wizard.py` wizard for report filters and actions.
- `pos_invoice_diclan/models/sales_report_compute.py` builds report payload.
- `pos_invoice_diclan/reports/sales_report_templates.xml` QWeb PDF template.
- `pos_invoice_diclan/reports/sales_report_action.xml` PDF report action.
- `pos_invoice_diclan/reports/sales_report_handler.py` report handler.
- `pos_invoice_diclan/views/*.xml` UI views and menus.
- `pos_invoice_diclan/security/ir.model.access.csv` access control.

## pos_product_colors key files
- `pos_product_colors/__manifest__.py` addon metadata, assets, and dependencies.
- `pos_product_colors/models/product.py` adds `pos_bg_color` to product template/product.
- `pos_product_colors/models/pos_loader.py` loads `pos_bg_color` in POS session loader.
- `pos_product_colors/views/product_template_view.xml` adds field to product form.
- `pos_product_colors/static/src/xml/pos_product_tile_color.xml` sets tile background.
- `pos_product_colors/static/src/scss/pos_product_fonts.scss` font sizing.
- `pos_product_colors/static/src/css/pos_hide_price.css` hides price in tile.
- `pos_product_colors/static/src/css/pos_product_center_text.css` centers product name.

## Development notes
- No AGENTS.md found in this repo; use `memory.md` and `context.md` as local guidance.
- Python and XML are typical Odoo patterns; keep changes consistent with Odoo 16/17 API.

## Session status
- Last step: created/confirmed `.ai/memory.md` and `.ai/context.md` with project summaries.
- No active coding task in progress; waiting for the next request.
