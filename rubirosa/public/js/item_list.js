// Copyright (c) 2020-2022, libracore and contributors
// For license information, please see license.txt

frappe.listview_settings['Item'] = {
    onload: function(listview) {
        listview.page.add_menu_item(__("Create EAN"), function() {
            var selected = listview.get_checked_items();
            create_bulk_ean(selected);
        });
    }
};

function create_bulk_ean(selected) {
    console.log(selected);
    frappe.call({
        "method": "rubirosa.rubirosa.gtin.create_bulk_ean",
        "args": {
            "selected": selected
        },
        "callback": function(response) {
            frappe.show_alert( __("Created") );
        }
    });

}
