# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# License: AGPL v3. See LICENCE

# import definitions
from __future__ import unicode_literals
import frappe
import json

@frappe.whitelist()
def get_user_info(user):
    orders = get_user_orders(user)
    invoices = get_user_invoices(user)
    marketing_material = get_marketing_material(orders)

    user_info = orders + invoices

    return {"user_info": user_info, "marketing_material": marketing_material}
    
def get_user_orders(user):

    sql_query = """
        SELECT 
        `tabSales Order`.`name` AS `sales_orders`
        FROM `tabContact`
        LEFT JOIN `tabDynamic Link` ON `tabContact`.`name` = `tabDynamic Link`.`parent`
            AND `tabDynamic Link`.`link_doctype` = "Customer"
        LEFT JOIN `tabSales Order` ON `tabDynamic Link`.`link_name` = `tabSales Order`.`customer` AND `tabSales Order`.`docstatus` = 1
        WHERE `tabContact`.`email_id` = '{user}'
    """.format(user=user)
    orders = frappe.db.sql(sql_query, as_dict = True)
    
    return orders

def get_user_invoices(user):

    sql_query = """
        SELECT 
        `tabSales Invoice`.`name` AS `sales_invoices`
        FROM `tabContact`
        LEFT JOIN `tabDynamic Link` ON `tabContact`.`name` = `tabDynamic Link`.`parent`
            AND `tabDynamic Link`.`link_doctype` = "Customer"
        LEFT JOIN `tabSales Invoice` ON `tabDynamic Link`.`link_name` = `tabSales Invoice`.`customer` AND `tabSales Invoice`.`docstatus` = 1
        WHERE `tabContact`.`email_id` = '{user}'
    """.format(user=user)
    invoices = frappe.db.sql(sql_query, as_dict = True)
    
    return invoices

def get_marketing_material(orders):

    order_names = [order['sales_orders'] for order in orders]
    orders_str = ', '.join(["'" + order + "'" for order in order_names])
    frappe.log_error("mm orders {0}".format(orders_str))
    sql_query = """
        SELECT
            `tabMarketing Material`.`name`,
            `tabMarketing Material`.`season`,
            `tabMarketing Material`.`item_code`,
            `tabMarketing Material`.`content`,
            `tabItem`.`variant_of`,
            `tabSales Order`.`name` AS `so`,
            `tabMarketing Material`.`image`
        FROM
            `tabMarketing Material`
        LEFT JOIN
            `tabSales Order` ON `tabSales Order`.`sales_season` = `tabMarketing Material`.`season`
        LEFT JOIN
            `tabSales Order Item` ON `tabSales Order Item`.`parent` = `tabSales Order`.`name`
        LEFT JOIN
            `tabItem` ON `tabItem`.`item_code` = `tabSales Order Item`.`item_code`
        WHERE
            (
                (`tabMarketing Material`.`season` IS NOT NULL AND `tabSales Order`.`name` IN ({orders}))
                OR
                (`tabMarketing Material`.`item_code` IS NOT NULL AND `tabItem`.`variant_of` = `tabMarketing Material`.`item_code`)
            )
    """.format(orders=orders_str)
    marketing_material = frappe.db.sql(sql_query, as_dict=True)

    return marketing_material

@frappe.whitelist()
def create_marketing_material(file_name, content=None):

    marketing_material = frappe.new_doc('Marketing Material')
    marketing_material.image = file_name
    marketing_material.content = content 
    
    try:
        marketing_material.insert()
        frappe.db.commit()
    except Exception as e:
        frappe.log_error("Marketing Material Creation Error", "{0}".format(e))
        
    return marketing_material.name
