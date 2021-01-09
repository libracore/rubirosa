// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Order Overview"] = {
    "filters": [
        {
            "fieldname":"sales_season",
            "label": __("Sales Season"),
            "fieldtype": "Link",
            "options": "Monthly Distribution",
            "reqd": 1
        },
        {
            "fieldname":"territory",
            "label": __("Territory"),
            "fieldtype": "Link",
            "options": "Territory"
        }
    ]
};
