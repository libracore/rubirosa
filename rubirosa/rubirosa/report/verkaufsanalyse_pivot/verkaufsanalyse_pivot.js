// Copyright (c) 2016-2023, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Verkaufsanalyse Pivot"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From date"),
            "fieldtype": "Date",
            "default": new Date().getFullYear() + "-01-01",
            "reqd": 1
        },
        {
            "fieldname": "end_date",
            "label": __("End date"),
            "fieldtype": "Date",
            "default" : frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "territory",
            "label": __("Territory"),
            "fieldtype": "Link",
            "options": "Territory"
        }
    ]
};
