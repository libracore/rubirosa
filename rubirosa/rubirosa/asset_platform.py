# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# License: AGPL v3. See LICENCE

# import definitions
from __future__ import unicode_literals
import frappe
import json


@frappe.whitelist()
def get_user_info(user):
    
    contact = frappe.get_value("Contact", {"email_id": user}, "name")
    if not contact:
        contact = frappe.get_value("Contact Email", {"email_id": user}, "parent")

    customer = frappe.get_value("Dynamic Link", filters={ "parenttype": "Contact", "link_doctype": "Customer", "parent": contact}, fieldname="link_name")
    
    orders = get_user_orders(customer)
    invoices = get_user_invoices(customer)

    user_info = orders + invoices

    return {"user_info": user_info }
    
def get_user_orders(customer):

    sql_query = """
        SELECT 
        `tabSales Order`.`name` AS `sales_orders`,
        `tabSales Order`.`delivery_date` AS `delivery_date`,
        `tabSales Order`.`delivery_status` AS `delivery_status`,
        `tabSales Order`.`per_delivered` AS `per_delivered`,
        `tabSales Order`.`transaction_date` AS `date`,
        `tabSales Order`.`language` AS `language`,
        '[]' AS `delivery_notes`
        FROM `tabSales Order`
        WHERE `tabSales Order`.`customer` = '{customer}'
        AND `tabSales Order`.`docstatus` = 1
        ORDER BY `tabSales Order`.`creation` DESC
        LIMIT 20
    """.format(customer=customer)
    orders = frappe.db.sql(sql_query, as_dict = True)
    
    # Add the respective DN to the Order
    for order in orders:
        dn_list = []
        if order['delivery_status'] != "Not Delivered":
            for delivery_note in get_so_delivery_notes(order.sales_orders):
                dn_list.append(delivery_note['delivery_note'])

            order['delivery_notes'] = dn_list
    
    return orders

def get_so_delivery_notes(sales_order):
    sql_query = """
        SELECT 
            `tabDelivery Note Item`.`parent` AS `delivery_note`
        FROM `tabDelivery Note Item`
        WHERE `tabDelivery Note Item`.`against_sales_order` = "{sales_order}"
        GROUP BY `tabDelivery Note Item`.`parent`
    """.format(sales_order=sales_order)
    
    delivery_note_list = frappe.db.sql(sql_query, as_dict=True)

    return delivery_note_list

def get_user_invoices(customer):
    sql_query = """
        SELECT 
        `tabSales Invoice`.`name` AS `sales_invoices`,
        `tabSales Invoice`.`due_date` AS `due_date`,
        `tabSales Invoice`.`status` AS `status`,
        `tabSales Invoice`.`posting_date` AS `date`,
        `tabSales Invoice`.`language` AS `language`
        FROM `tabSales Invoice`
        WHERE `tabSales Invoice`.`customer` = '{customer}'
        ORDER BY `tabSales Invoice`.`creation` DESC
        LIMIT 20
    """.format(customer=customer)
    invoices = frappe.db.sql(sql_query, as_dict = True)
    
    return invoices

@frappe.whitelist()
def get_marketing_material(orders=None, limit=20, offset=0):
    # Create a list to store unique marketing materials
    unique_marketing_materials = []
    total_unique_marketing_materials_ids = []
    total_unique_marketing_materials = 0
    
    select_maketing_material = """
        SELECT
            `tabMarketing Material`.`name`,
            `tabMarketing Material`.`season`,
            `tabMarketing Material`.`item_code`,
            `tabMarketing Material`.`content`,
            `tabMarketing Material`.`image`,
            `tabMarketing Material`.`category`,
        GROUP_CONCAT(DISTINCT `tabFile`.`file_url`) AS `attachment_urls`
        FROM
            `tabMarketing Material`
        LEFT JOIN `tabFile` ON `tabFile`.`attached_to_name` = `tabMarketing Material`.`name` AND `tabFile`.`attached_to_doctype` = 'Marketing Material' """

    if orders is not None:
        orders = orders.split(",")[:-1]
        for order in orders:
            orders_query = """
                {select_maketing_material}
                LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = "{order}"
                LEFT JOIN `tabSales Order Item` ON `tabSales Order Item`.`parent` = `tabSales Order`.`name`
                LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabSales Order Item`.`item_code`
                WHERE
                    (
                        `tabMarketing Material`.`season` = `tabSales Order`.`sales_season`
                        OR `tabMarketing Material`.`item_code` LIKE CONCAT(LEFT(`tabSales Order Item`.`item_code`, LENGTH(`tabSales Order Item`.`item_code`) - 6), '%')
                    )
                GROUP BY `tabMarketing Material`.`name`
                ORDER BY `tabMarketing Material`.`creation` DESC """.format(order=order, select_maketing_material=select_maketing_material)
                
            sql_query = """
				{orders_query}
                LIMIT {limit} OFFSET {offset}
                """.format(orders_query=orders_query, limit=limit, offset=offset)

            total_orders_marketing_materials = frappe.db.sql(orders_query, as_dict=True)
            marketing_material = frappe.db.sql(sql_query, as_dict=True)
            
            if marketing_material:

                for material in total_orders_marketing_materials:
                    if material['name'] not in [m['name'] for m in total_unique_marketing_materials_ids]:
                        # Creating a dictionary for each Marketing Material
                        marketing_dict = {'name': material['name'] }
                        total_unique_marketing_materials_ids.append(marketing_dict)
                total_unique_marketing_materials = len(total_unique_marketing_materials_ids)

                for material in marketing_material:
                    if material['name'] not in [m['name'] for m in unique_marketing_materials]:
                        # Creating a dictionary for each Marketing Material
                        marketing_dict = {
                            'name': material['name'],
                            'season': material['season'],
                            'item_code': material['item_code'],
                            'content': material['content'],
                            'image': material['image'],
                            'attachment_urls': material['attachment_urls']
                        }
                        unique_marketing_materials.append(marketing_dict)

    else:
        all_mm_query = """
            {select_maketing_material}
            GROUP BY `tabMarketing Material`.`name`
            ORDER BY `tabMarketing Material`.`creation` DESC
            """.format(select_maketing_material=select_maketing_material)
			
        sql_query = """
			{all_mm_query}
            LIMIT {limit} OFFSET {offset}
            """.format(all_mm_query=all_mm_query, limit=limit, offset=offset)

        total_mm_sql_query = frappe.db.sql(all_mm_query, as_dict=True) 
        marketing_material = frappe.db.sql(sql_query, as_dict=True)
         
        if marketing_material:
            unique_marketing_materials = marketing_material
            total_unique_marketing_materials = len(total_mm_sql_query)
            
    return unique_marketing_materials, total_unique_marketing_materials
