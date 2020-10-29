// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('MS Direct Settings', {
    refresh: function(frm) {
        // filter for delivery note print formats
        cur_frm.fields_dict['dn_print_format'].get_query = function(doc) {
             return {
                 filters: {
                     "doc_type": "Delivery Note"
                 }
             }
        }
        cur_frm.fields_dict['sinv_print_format'].get_query = function(doc) {
             return {
                 filters: {
                     "doc_type": "Delivery Note"
                 }
             }
        }
    }
});
