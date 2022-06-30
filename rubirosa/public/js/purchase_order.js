frappe.ui.form.on("Purchase Order", {
    on_submit: function(frm) {
        //send_to_msdirect(frm);            // disabled: MS Direct cannot process part deliveries
    }
});

function send_to_msdirect(frm) {
    frappe.call({
        "method": "rubirosa.rubirosa.msdirect.write_purchase_order",
        "args": {
            "purchase_order": frm.doc.name
        },
        "callback": function(response) {
            frappe.show_alert( __("Sent to MS Direct") );
        }
    });
}
