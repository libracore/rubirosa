frappe.ui.form.on("Purchase Receipt", {
    on_submit: function(frm) {
        // send_to_msdirect(frm);   // disabled 2022-07-22 (replaced by transfer file)
    }
});

function send_to_msdirect(frm) {
    frappe.call({
        "method": "rubirosa.rubirosa.msdirect.write_purchase_receipt",
        "args": {
            "purchase_receipt": frm.doc.name
        },
        "callback": function(response) {
            frappe.show_alert( __("Sent to MS Direct") );
        }
    });
}
