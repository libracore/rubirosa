frappe.ui.form.on("Delivery Note", {
    /* 2023-12-13 disabled MS Direct
     * on_submit: function(frm) {
        var warehouse = frm.doc.items[0].warehouse;
        if ((frm.doc.is_return === 0) && (warehouse === "Stock EU - RMG")) {
            send_to_msdirect(frm);
        }
    } */
});

function send_to_msdirect(frm) {
    frappe.call({
        'method': 'rubirosa.rubirosa.msdirect.enqueue_write',
        'args': {
            'command': 'rubirosa.rubirosa.msdirect.write_delivery_note',
            'kwargs': {
                'delivery_note': frm.doc.name
            }
        },
        "callback": function(response) {
            frappe.show_alert( __("Sent to MS Direct") );
        }
    });
}
