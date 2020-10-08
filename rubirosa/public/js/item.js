frappe.ui.form.on("Item", {
    validate: function(frm) {
        if ((!frm.doc.__islocal) && (frm.doc.is_stock_item)) {
            send_to_msdirect(frm);
        }
    }
});

function send_to_msdirect(frm) {
    frappe.call({
        "method": "rubirosa.rubirosa.msdirect.write_item",
        "args": {
            "item_code": frm.doc.item_code
        },
        "callback": function(response) {
            frappe.show_alert( __("Sent to MS Direct") );
        }
    });
}
