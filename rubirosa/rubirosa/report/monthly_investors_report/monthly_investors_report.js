// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Investors Report"] = {
    "filters": [
        {
            "fieldname":"year",
            "label": __("Year"),
            "fieldtype": "Int",
            "default": new Date().getFullYear(),
            "reqd": 1
        },
        {
            "fieldname":"month",
            "label": __("Month"),
            "fieldtype": "Int",
            "default": new Date().getMonth() + 1,
            "reqd": 1
        },
        {
            "fieldname":"company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("company"),
            "reqd": 1
        }
    ]
};
