odoo.define('pos_receipt_address.models', function(require) {
    'use strict';

    var { Order } = require('point_of_sale.models');
    var Registries = require('point_of_sale.Registries');

    const USD_RATE = 89000;

    const CustomOrder = (Order) => class CustomOrder extends Order {
        export_for_printing() {
            var result = super.export_for_printing(...arguments);
            result.client = this.get_partner();

            const total_lbp = result.total_with_tax || 0;
            result.total_usd = total_lbp / USD_RATE;
            return result;
        }
    };

Registries.Model.extend(Order, CustomOrder);
});