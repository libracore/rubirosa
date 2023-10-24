# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# License: AGPL v3. See LICENCE

# import definitions
from __future__ import unicode_literals
import frappe
import json
from frappe.utils.file_manager import save_file

@frappe.whitelist()
def get_user_info(user):
    orders = get_user_orders(user)
    invoices = get_user_invoices(user)
    marketing_material = get_marketing_material(orders, user)

    user_info = orders + invoices

    return {"user_info": user_info, "marketing_material": marketing_material}
    
def get_user_orders(user):

    sql_query = """
        SELECT 
        `tabSales Order`.`name` AS `sales_orders`,
        `tabSales Order`.`delivery_date` AS `delivery_date`,
        `tabSales Order`.`delivery_status` AS `delivery_status`
        FROM `tabContact`
        LEFT JOIN `tabDynamic Link` ON `tabContact`.`name` = `tabDynamic Link`.`parent`
            AND `tabDynamic Link`.`link_doctype` = "Customer"
        LEFT JOIN `tabSales Order` ON `tabDynamic Link`.`link_name` = `tabSales Order`.`customer` AND `tabSales Order`.`docstatus` = 1
        WHERE `tabContact`.`email_id` = '{user}'
        ORDER BY `tabSales Order`.`creation` DESC
    """.format(user=user)
    orders = frappe.db.sql(sql_query, as_dict = True)
    
    return orders

def get_user_invoices(user):

    sql_query = """
        SELECT 
        `tabSales Invoice`.`name` AS `sales_invoices`,
        `tabSales Invoice`.`due_date` AS `due_date`,
        `tabSales Invoice`.`status` AS `status`
        FROM `tabContact`
        LEFT JOIN `tabDynamic Link` ON `tabContact`.`name` = `tabDynamic Link`.`parent`
            AND `tabDynamic Link`.`link_doctype` = "Customer"
        LEFT JOIN `tabSales Invoice` ON `tabDynamic Link`.`link_name` = `tabSales Invoice`.`customer` AND `tabSales Invoice`.`docstatus` = 1
        WHERE `tabContact`.`email_id` = '{user}'
        ORDER BY `tabSales Invoice`.`creation` DESC
    """.format(user=user)
    invoices = frappe.db.sql(sql_query, as_dict = True)
    
    return invoices
 
def get_marketing_material(orders, user):
    # Create a list to store unique marketing materials
    unique_marketing_materials = []

    for order in orders:
        sql_query = """
            SELECT
                `tabMarketing Material`.`name`,
                `tabMarketing Material`.`season`,
                `tabMarketing Material`.`item_code`,
                `tabMarketing Material`.`content`,
                `tabMarketing Material`.`image`
            FROM
                `tabMarketing Material`
            LEFT JOIN
                `tabSales Order` ON `tabSales Order`.`name` = "{order}"
            LEFT JOIN
                `tabSales Order Item` ON `tabSales Order Item`.`parent` = `tabSales Order`.`name`
            LEFT JOIN
                `tabItem` ON `tabItem`.`item_code` = `tabSales Order Item`.`item_code`
            WHERE
                (
                    `tabMarketing Material`.`season` = `tabSales Order`.`sales_season`
                    OR `tabItem`.`variant_of` = `tabMarketing Material`.`item_code`
                    OR `tabMarketing Material`.`owner` = '{user}'
                )
            GROUP BY `tabMarketing Material`.`name`
            ORDER BY `tabMarketing Material`.`creation` DESC
        """.format(order=order['sales_orders'], user=user)

        marketing_material = frappe.db.sql(sql_query, as_dict=True)

        if marketing_material:
            unique_marketing_materials.extend(marketing_material)

    return unique_marketing_materials
