# Project Memory

## Overview
- Repository contains two Odoo addons for POS: `pos_invoice_diclan` (Odoo 17) and `pos_product_colors` (Odoo 16).
- Root path: `/mnt/c/odoo_final/custom-addons`.

## pos_invoice_diclan (Odoo 17)
- Purpose: Create and log POS invoices, plus generate a PDF sales report from logs.
- Models:
  - `pos.invoice.log` and `pos.invoice.log.line` for storing invoice snapshots.
  - `pos.sales.report.wizard` to filter/preview/print reports.
  - `pos.sales.report.compute` to build report payloads.
  - `pos.order` is inherited to create invoices and logs on payment.
- Report:
  - QWeb PDF template: `pos_invoice_diclan.sales_logs_pdf_document`.
  - Wizard actions: preview list and print PDF.
- Menus:
  - POS Invoice Logs list under POS root.
  - Diclan Reporting menu for the sales report wizard.

## pos_product_colors (Odoo 16)
- Purpose: Add a per-product POS tile background color and tweak POS grid text styling.
- Fields:
  - `product.template.pos_bg_color`, related on `product.product`.
- POS loader:
  - Adds `pos_bg_color` to loaded product fields.
- POS UI assets:
  - XML template extends `point_of_sale.ProductItem` to set tile background.
  - CSS/SCSS for larger fonts, hide price, and center product name.

## Notable behaviors
- `pos.order.write` in `pos_invoice_diclan` creates a customer invoice and a log when the order becomes paid/invoiced/done.
- Invoice log totals are computed from line subtotals with currency rounding.
- Sales report totals are computed from log lines and rendered in QWeb.
