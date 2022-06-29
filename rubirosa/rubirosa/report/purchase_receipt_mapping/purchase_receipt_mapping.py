# Copyright (c) 2022, libracore and contributors
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
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 200},
        {"label": _("Item name"), "fieldname": "item_name", "fieldtype": "Data", "width": 100},
        {"label": _("PO"), "fieldname": "purchase_order", "fieldtype": "Link", "options": "Purchase Order", "width": 100},
        {"label": _("PO Qty"), "fieldname": "po_qty", "fieldtype": "Float", "width": 75},
        {"label": _("PR Qty"), "fieldname": "pr_qty", "fieldtype": "Float", "width": 75},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 80},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("SO Qty"), "fieldname": "so_qty", "fieldtype": "Float", "width": 75},
        {"label": _("Deliverred Qty"), "fieldname": "del_qty", "fieldtype": "Float", "width": 75},
    ]
    
def get_data(filters):       
    sql_query = """SELECT 
            `tabPurchase Receipt Item`.`item_code` AS `item_code`,
            `tabPurchase Receipt Item`.`item_name` AS `item_name`,
            `tabPurchase Receipt Item`.`purchase_order` AS `purchase_order`,
            `tabPurchase Order Item`.`qty` AS `po_qty`,
            `tabPurchase Receipt Item`.`qty` AS `pr_qty`,
            `tabSales Order Item`.`parent` AS `sales_order`,
            `tabSales Order Item`.`qty` AS `so_qty`,
            `tabSales Order Item`.`delivered_qty` AS `del_qty`,
            `tabSales Order`.`customer` AS `customer`
        FROM `tabPurchase Receipt Item`
        LEFT JOIN `tabPurchase Order Item` ON 
            `tabPurchase Order Item`.`name` = `tabPurchase Receipt Item`.`purchase_order_item`
        LEFT JOIN `tabSales Order Item` ON
            `tabSales Order Item`.`item_code` = `tabPurchase Receipt Item`.`item_code`
            AND `tabPurchase Order Item`.`sales_order_trace` LIKE CONCAT("%", `tabSales Order Item`.`parent`, "%")
            AND `tabSales Order Item`.`docstatus` = 1
        LEFT JOIN `tabSales Order` ON
            `tabSales Order`.`name` = `tabSales Order Item`.`parent`
        WHERE `tabPurchase Receipt Item`.`parent` = "{0}"
    """.format(filters.purchase_receipt)
    
    data = frappe.db.sql(sql_query, as_dict=True)
    
    return data
