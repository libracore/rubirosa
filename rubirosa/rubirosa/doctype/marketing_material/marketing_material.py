# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MarketingMaterial(Document):
    pass

@frappe.whitelist()
def push_notifications(item=None, season=None):

    sql_query = """
        SELECT 
            `tabUser`.`email`
        FROM `tabContact`
        LEFT JOIN `tabDynamic Link` ON `tabContact`.`name` = `tabDynamic Link`.`parent`
            AND `tabDynamic Link`.`link_doctype` = "Customer"
        LEFT JOIN `tabSales Order` ON `tabDynamic Link`.`link_name` = `tabSales Order`.`customer` 
        LEFT JOIN `tabSales Order Item` ON `tabSales Order Item`.`parent` = `tabSales Order`.`name`
        LEFT JOIN `tabUser` ON `tabContact`.`email_id` = `tabUser`.`email`
        WHERE (`tabSales Order`.`sales_season` = '{season}' OR '{item}' LIKE CONCAT(LEFT(`tabSales Order Item`.`item_code`, LENGTH(`tabSales Order Item`.`item_code`) - 6), '%'))
        AND `tabSales Order`.`contact_person` = `tabContact`.`name`
        AND `tabUser`.`name` IS NOT NULL
        GROUP BY `tabUser`.`name`
        ORDER BY `tabSales Order`.`creation` DESC
    """.format(item=item, season=season)
    
    contacts = frappe.db.sql(sql_query, as_dict=True)
    users_email = []

    for contact in contacts:
        users_email.append(contact.email)

    return users_email
