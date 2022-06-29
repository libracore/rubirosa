// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Receipt Mapping"] = {
    "filters": [
        {
            "fieldname":"purchase_receipt",
            "label": __("Purchase Receipt"),
            "fieldtype": "Link",
            "options": "Purchase Receipt",
            "reqd": 1
        }
    ]
};
