// Copyright (c) 2023, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Marketing Material', {
	refresh: function(frm) {
		// display only items that are Templates
        frm.fields_dict['item_code'].get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                    ['Item', 'has_variants', '=', 1]
                ]
            };
        };
	}
});
