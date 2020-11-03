frappe.ui.form.on("Delivery Note", {
    on_submit: function(frm) {
        var warehouse = frm.doc.items[0].warehouse;
        if (warehouse === "Stock EU - RMG") {
            send_to_msdirect(frm);
        }
    }
});

function send_to_msdirect(frm) {
    frappe.call({
        "method": "rubirosa.rubirosa.msdirect.write_delivery_note",
        "args": {
            "delivery_note": frm.doc.name
        },
        "callback": function(response) {
            frappe.show_alert( __("Sent to MS Direct") );
        }
    });
}
