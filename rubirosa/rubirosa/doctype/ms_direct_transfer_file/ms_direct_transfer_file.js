// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('MS Direct Transfer File', {
    refresh: function(frm) {
        if (!frm.doc.date) {
            cur_frm.set_value("date", new Date());
        }
        
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__("Send"), function() {
                send_file(frm);
            });
        }
    },
    validate: function(frm) {
        // check if all suppliers are the same
        if ((frm.doc.purchase_orders) && (frm.doc.purchase_orders.length > 0)) {
            var supplier = null;
            for (var i = 0; i < frm.doc.purchase_orders.length; i++) {
                if (!supplier) {
                    supplier = frm.doc.purchase_orders[i].supplier;
                } else {
                    if (supplier !== frm.doc.purchase_orders[i].supplier) {
                        frappe.msgprint( __("Please set use only POs from one supplier"), __("Validation") );
                        frappe.validated = false;
                    }
                }
            }
        }
    }
});

function send_file(frm) {
    if (frm.doc.file_type === "Purchase Order") {
        frappe.call({
            'method': 'rubirosa.rubirosa.msdirect.send_multiple_pos',
            'args': {
                'msd_transfer_file': frm.doc.name
            },
            'callback': function(r) {
                frappe.show_alert( __("Sent") );
            }
        });
    } else {
        frappe.msgprint( __("Not implemented") );
    }
}
