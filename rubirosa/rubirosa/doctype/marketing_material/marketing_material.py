# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MarketingMaterial(Document):
    pass

@frappe.whitelist()
def fix_attachment(name, url):
    # ~ Making sure that the attachment_image gets attach when is a new doc
    file_doc = frappe.get_all("File", filters=[["attached_to_doctype", "=", "Marketing Material"], ["file_url", "=", url], ["attached_to_name", "like", "New Marketing Material%"]])
    if len(file_doc) > 0:
         doc = frappe.get_doc("File", file_doc[0].name)
         frappe.db.set(doc, 'attached_to_name', name)
         doc.save()
    
@frappe.whitelist()
def push_notifications(reason=None, item=None, season=None):
    reason_sql = None
    if reason == "Item":
        reason_sql = """ '{item}' LIKE CONCAT(LEFT(`tabSales Order Item`.`item_code`, LENGTH(`tabSales Order Item`.`item_code`) - 6), '%') """.format(item=item)
    elif reason == "Season":
        reason_sql = """ `tabSales Order`.`sales_season` = '{season}' """.format(season=season)
        
    sql_query = """
        SELECT 
            `tabUser`.`email`
        FROM `tabContact`
        LEFT JOIN `tabDynamic Link` ON `tabContact`.`name` = `tabDynamic Link`.`parent`
            AND `tabDynamic Link`.`link_doctype` = "Customer"
        LEFT JOIN `tabSales Order` ON `tabDynamic Link`.`link_name` = `tabSales Order`.`customer` 
        LEFT JOIN `tabSales Order Item` ON `tabSales Order Item`.`parent` = `tabSales Order`.`name`
        LEFT JOIN `tabUser` ON `tabContact`.`email_id` = `tabUser`.`email`
        WHERE {reason_sql}
        AND `tabSales Order`.`contact_person` = `tabContact`.`name`
        AND `tabUser`.`name` IS NOT NULL
        AND `tabContact`.`unsubscribed` = 0
        GROUP BY `tabUser`.`name`
        ORDER BY `tabSales Order`.`creation` DESC
    """.format(reason_sql=reason_sql)
    
    contacts = frappe.db.sql(sql_query, as_dict=True)
    users_email = []

    for contact in contacts:
        users_email.append(contact.email)

    return users_email
