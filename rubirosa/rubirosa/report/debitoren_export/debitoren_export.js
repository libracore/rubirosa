// Copyright (c) 2016, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Debitoren Export"] = {
    "filters": [
        {
            "fieldname": "sinv_type",
            "label": __("Invoice Type"),
            "fieldtype": "Select",
            "options": "\nInvoices\nReturns",
            "reqd": 1
        }
    ]
};
