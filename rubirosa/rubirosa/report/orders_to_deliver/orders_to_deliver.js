// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Orders to Deliver"] = {
    "filters": [
        {
            "fieldname":"sales_season",
            "label": __("Sales Season"),
            "fieldtype": "Link",
            "options": "Monthly Distribution"
        },
        {
            "fieldname":"territory",
            "label": __("Territory"),
            "fieldtype": "Link",
            "options": "Territory"
        }
    ]
};
