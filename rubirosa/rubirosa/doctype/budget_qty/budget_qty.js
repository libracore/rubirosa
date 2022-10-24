// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Budget Qty', {
    refresh: function(frm) {
        if (frm.doc.__islocal) {
            cur_frm.set_value("year", (new Date()).getFullYear() + 1);
            for (var m = 1; m < 13; m++) {
                var child = cur_frm.add_child('qtys');
                frappe.model.set_value(child.doctype, child.name, 'month', m);
                child = cur_frm.add_child('qtys_online');
                frappe.model.set_value(child.doctype, child.name, 'month', m);
            }
            cur_frm.refresh_fields('qtys');
        }   
    }
});
