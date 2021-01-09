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
        {"label": _("Street"), "fieldname": "street", "fieldtype": "Data", "width": 100},
        {"label": _("Pincode"), "fieldname": "pincode", "fieldtype": "Data", "width": 100},
        {"label": _("City"), "fieldname": "city", "fieldtype": "Data", "width": 100},
        {"label": _("Territory"), "fieldname": "territory", "fieldtype": "Link", "options": "Territory", "width": 100},
        {"label": _("Customer Group"), "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group", "width": 100},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": _("Amount"), "fieldname": "order_amount", "fieldtype": "Currency", "width": 100},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": _("Purchase Order"), "fieldname": "purchase_order", "fieldtype": "Link", "options": "Purchase Order", "width": 100},
        {"label": _("Check"), "fieldname": "check", "fieldtype": "Data", "width": 100}
    ]
    
def get_data(filters):
    conditions = ""
    if (filters.territory):
        conditions += " AND `tabCustomer`.`territory` = '{t}'".format(t=filters.territory)
        
    sql_query = """SELECT 
                     `raw`.`name` AS `customer`,
                     `raw`.`customer_group` AS `customer_group`,
                     `raw`.`territory` AS `territory`,
                     `tabAddress`.`address_line1` AS `street`,
                     `tabAddress`.`pincode` AS `pincode`,
                     `tabAddress`.`city` AS `city`,
                     `tabSales Order`.`name` AS `sales_order`,
                     `tabSales Order`.`total_qty` AS `qty`,
                     `tabSales Order`.`base_net_total` AS `order_amount`,
                     (SELECT `tabPurchase Order Item`.`parent`
                      FROM `tabPurchase Order Item`
                      WHERE `tabPurchase Order Item`.`sales_order_trace` LIKE CONCAT("%", `tabSales Order`.`name`, "%")
                      LIMIT 1) AS `purchase_order`,
                     (SELECT IF(IFNULL(`tabSales Order`.`total_qty`, 0) <= IFNULL(SUM(`tabPurchase Order Item`.`qty`), 0), "<span style='color:green; '>OK</span>", "<b><span style='color:red; '>NOK</span></b>")
                      FROM `tabPurchase Order Item`
                      WHERE `tabPurchase Order Item`.`sales_order_trace` LIKE CONCAT("%", `tabSales Order`.`name`, "%")
                      ) AS `check`
                   FROM (
                    SELECT `tabCustomer`.`name`, 
                      `tabCustomer`.`customer_group` AS `customer_group`,
                      `tabCustomer`.`territory` AS `territory`,
                      `tabAddress`.`name` AS `address`
                    FROM `tabCustomer`
                    LEFT JOIN `tabDynamic Link` AS `tDL` ON `tDL`.`link_doctype` = "Customer" 
                                                        AND `tDL`.`link_name` = `tabCustomer`.`name`
                                                        AND `tDL`.`parenttype` = "Address"
                    LEFT JOIN `tabAddress` ON `tabAddress`.`name` = `tDL`.`parent`
                    WHERE `tabAddress`.`is_primary_address` = 1
                      AND `tabCustomer`.`customer_group` LIKE "%Retail%"
                      AND `tabCustomer`.`disabled` = 0
                      {conditions}
                   ) AS `raw`     
                   LEFT JOIN `tabAddress` ON `tabAddress`.`name` = `raw`.`address`
                   LEFT JOIN `tabSales Order` ON `tabSales Order`.`customer` = `raw`.`name`
                                             AND `tabSales Order`.`sales_season` = "{season}"
                     ;
      """.format(season=filters.sales_season, conditions=conditions)
    data = frappe.db.sql(sql_query, as_dict=1)

    # find totals
    totals = {'order_qty': 0, 'order_amount': 0}
    for row in data:
        totals['order_qty'] += row['qty'] or 0
        totals['order_amount'] += row['order_amount'] or 0

    # add differential amount as row
    data.append({
        'customer': "",
        'street': "<b>Total</b>",
        'pincode': "",
        'city': "",
        'territory': filters.territory or "",
        'customer_group': "",
        'qty': totals['order_qty'],
        'order_amount': totals['order_amount'],
        'sales_order': None,
        'purchase_order': None,
        'check': ""
    })
    
    # find targets
    if filters.territory:
        territory = filters.territory
    else:
        territory = "%"
    sql_query = """SELECT SUM(`target_qty`) AS `qty`, SUM(`target_amount`) AS `amount`
        FROM `tabTarget Detail`
        LEFT JOIN `tabSales Partner` ON `tabSales Partner`.`name` = `tabTarget Detail`.`parent`

        WHERE `tabTarget Detail`.`distribution_id` = "{season}"
          AND `tabSales Partner`.`territory` LIKE "{territory}";""".format(season=filters.sales_season, territory=territory)
    targets = frappe.db.sql(sql_query, as_dict=True)
    
    if len(targets) > 0:
        achievement = 0
        try:
            if targets[0]['qty'] > 0:
                achievement = round(100 * totals['order_qty'] / targets[0]['qty'], 0)
        except:
            achievement = 0
        # add differential amount as row
        data.append({
            'customer': "",
            'street': "Target",
            'pincode': "{0}%".format(achievement),
            'city': "",
            'territory': filters.territory or "",
            'customer_group': "",
            'qty': targets[0]['qty'],
            'order_amount': targets[0]['amount'],
            'sales_order': None,
            'purchase_order': None,
            'check': ""
        })
    
    return data
