cur_frm.dashboard.add_transactions([
    { 
        'label': __('Documents'),
        'items': [
            'Customer Visit Report'
        ]
    }
]);

frappe.ui.form.on("Customer", {
    refresh: function(frm) {
        frm.add_custom_button(__("Statistics"), function() {
            frappe.set_route("query-report", "Customer Statistics", {"customer": frm.doc.name});
        });
    }
});
