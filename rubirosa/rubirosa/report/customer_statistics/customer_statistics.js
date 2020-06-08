// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Statistics"] = {
	"filters": [
        {
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
        }
	]
};
