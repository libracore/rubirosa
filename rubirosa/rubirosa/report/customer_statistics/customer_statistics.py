# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)

    return columns, data
    
def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 100},
        {"label": _("Total revenue"), "fieldname": "total_revenue", "fieldtype": "Currency", "width": 100},
        {"label": _("Total qty"), "fieldname": "total_qty", "fieldtype": "Float", "precision": 2, "width": 100},
        {"label": _("First sale"), "fieldname": "first_sale", "fieldtype": "Date", "width": 100}
    ]
    
def get_data(filters):
    if not filters.customer:
        filters.customer = "%"
        
    sql_query = """SELECT
                `customer`,
                `customer_name`,
                SUM(`base_net_total`) AS `total_revenue`,
                SUM(`total_qty`) AS `total_qty`,
                MIN(`posting_date`) AS `first_sale`
            FROM `tabSales Invoice`
            WHERE `docstatus` = 1
                AND `customer` LIKE '{customer}'
            GROUP BY `customer`
            ORDER BY SUM(`base_net_total`) DESC;
      """.format(customer=filters.customer)

    data = frappe.db.sql(sql_query, as_dict=1)

    return data
