# Copyright (c) 2013-2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    # prepare filters
    filters = frappe._dict(filters or {})
    if not filters.from_date:
        filters.from_date = "2000-01-01"
    if not filters.end_date:
        filters.end_date = "2999-01-01"
    # prepare columns
    columns = get_columns(filters)
    # load data
    data = get_data(filters)

    return columns, data
    
def get_columns(filters):
    columns = [
        {"label": _("Item"), "fieldname": "item_name", "fieldtype": "Data", "width": 200}
    ]
    for g in get_customer_groups(filters):
        columns.append(
            {"label": "{0} (Qty)".format(g['customer_group']), "fieldname": "qty_" + g['shortcode'], "fieldtype": "Float", "width": 100}
        )
        columns.append(
            {"label": "{0} (Amount)".format(g['customer_group']), "fieldname": "amount_" + g['shortcode'], "fieldtype": "currency", "width": 100}
        )        
    return columns
    
def get_data(filters):
    # prepare pivot fields
    pivot = ""
    for g in get_customer_groups(filters):
        pivot += """
            , (SELECT SUM(`qty`)
                   FROM `tabSales Invoice Item` AS `tSII`
                   JOIN `tabSales Invoice` AS `tSI` ON `tSI`.`name` = `tSII`.`parent`
                   WHERE `tSI`.`customer_group` = "{customer_group}" 
                    AND `tSII`.`item_name` = `tabSales Invoice Item`.`item_name`
                    AND `tSI`.`posting_date` >= "{from_date}"
                    AND `tSI`.`posting_date` <= "{end_date}") AS `qty_{shortcode}`
             , (SELECT SUM(`amount`)
                   FROM `tabSales Invoice Item` AS `tSII`
                   JOIN `tabSales Invoice` AS `tSI` ON `tSI`.`name` = `tSII`.`parent`
                   WHERE `tSI`.`customer_group` = "{customer_group}" 
                    AND `tSII`.`item_name` = `tabSales Invoice Item`.`item_name`
                    AND `tSI`.`posting_date` >= "{from_date}"
                    AND `tSI`.`posting_date` <= "{end_date}") AS `amount_{shortcode}`
        """.format(from_date=filters.from_date, end_date=filters.end_date,
            customer_group=g['customer_group'], shortcode=g['shortcode'])     
    
    sql_query = """SELECT 
                      `tabSales Invoice Item`.`item_name`
                      {pivot}
                    FROM `tabSales Invoice Item`
                    JOIN `tabSales Invoice` ON `tabSales Invoice`.`name` = `tabSales Invoice Item`.`parent`
                    WHERE 
                      `tabSales Invoice`.`posting_date` >= "{from_date}"
                      AND `tabSales Invoice`.`posting_date` <= "{end_date}"
                    GROUP BY `tabSales Invoice Item`.`item_name`
      """.format(from_date=filters.from_date, end_date=filters.end_date, pivot=pivot)

    data = frappe.db.sql(sql_query, as_dict=True)

    return data

def get_customer_groups(filters):
    # prepare customer groups
    customer_group_query = """SELECT `tabSales Invoice`.`customer_group`
                    FROM `tabSales Invoice`
                    WHERE `tabSales Invoice`.`posting_date` >= "{from_date}"
                      AND `tabSales Invoice`.`posting_date` <= "{end_date}"
                    GROUP BY `tabSales Invoice`.`customer_group`;""".format(from_date=filters.from_date, end_date=filters.end_date)
    customer_groups = frappe.db.sql(customer_group_query, as_dict=True)
    for g in customer_groups:
        g['shortcode'] = remove_special_chars(g['customer_group'].lower())
    return customer_groups
        
def remove_special_chars(s):
    alphanumeric = ""
    for character in s:
        if character.isalnum():
            alphanumeric += character
    return alphanumeric
