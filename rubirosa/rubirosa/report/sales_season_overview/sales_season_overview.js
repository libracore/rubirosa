// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Season Overview"] = {
    "filters": [
        {
            "fieldname":"monthly_distribution",
            "label": __("Sales Season"),
            "fieldtype": "Link",
            "options": "Monthly Distribution",
            "reqd": 1
        }
    ]
};
