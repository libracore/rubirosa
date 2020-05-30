// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Liquidity Plan"] = {
	"filters": [
        {
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Int",
			"default": new Date().getFullYear(),
            "reqd": 1
        }
	]
};
