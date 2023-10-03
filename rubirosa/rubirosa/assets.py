# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# License: AGPL v3. See LICENCE

# import definitions
from __future__ import unicode_literals
import frappe
import json

@frappe.whitelist()
def get_user_info(user):

    sql_query = """
        SELECT 
		`tabSales Order`.`name` AS `sales_orders`
		FROM `tabContact`
		LEFT JOIN `tabDynamic Link` ON `tabContact`.`name` = `tabDynamic Link`.`parent`
			AND `tabDynamic Link`.`link_doctype` = "Customer"
		LEFT JOIN `tabSales Order` ON `tabDynamic Link`.`link_name` = `tabSales Order`.`customer` AND `tabSales Order`.`docstatus` > 0
		WHERE `tabContact`.`email_id` = '{user}'
    """.format(user=user)
    data = frappe.db.sql(sql_query, as_dict = True)
    
    return data
