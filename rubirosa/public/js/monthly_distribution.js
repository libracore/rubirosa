frappe.ui.form.on("Monthly Distribution", {
    refresh: function(frm) {
        frm.add_custom_button(__("Export"), function() {
            frappe.set_route("query-report", "Sales Season Overview", {"monthly_distribution": frm.doc.name});
        });
    }
});
