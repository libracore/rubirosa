# Copyright (c) 2020-2022, libracore and contributors
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
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 80},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("Territory"), "fieldname": "territory", "fieldtype": "Link", "options": "Territory", "width": 100},
        {"label": _("Sales Season"), "fieldname": "sales_season", "fieldtype": "Link", "options": "Monthly Distribution", "width": 150},
        {"label": _("Volume"), "fieldname": "volume", "fieldtype": "Currency", "width": 100},
        {"label": _("Delivered %"), "fieldname": "delivered_percent", "fieldtype": "Percent", "width": 100},
        {"label": _(""), "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]
    
def get_data(filters):
    conditions = ""
    if (filters.territory):
        conditions += " AND `tabCustomer`.`territory` = '{t}'".format(t=filters.territory)
    if (filters.sales_season):
        conditions += " AND `tabSales Order`.`sales_season` = '{t}'".format(t=filters.sales_season)
        
    sql_query = """SELECT 
                     `tabSales Order`.`name` AS `sales_order`,
                     `tabSales Order`.`status` AS `status`,
                     `tabSales Order`.`customer` AS `customer`,
                     `tabCustomer`.`territory` AS `territory`,
                     `tabSales Order`.`sales_season` AS `sales_season`,
                     `tabSales Order`.`base_net_total` AS `volume`,
                     `tabSales Order`.`per_delivered` AS `delivered_percent`
                   FROM `tabSales Order`    
                   LEFT JOIN `tabCustomer` ON `tabSales Order`.`customer` = `tabCustomer`.`name`
                   WHERE 
                    `tabSales Order`.`docstatus` < 2
                    AND `tabSales Order`.`per_delivered` < 100
                    AND `tabSales Order`.`status` != "Completed"
                    AND `tabSales Order`.`status` != "Closed"
                    {conditions}
                     ;
      """.format(conditions=conditions)
    data = frappe.db.sql(sql_query, as_dict=1)
        
    return data
