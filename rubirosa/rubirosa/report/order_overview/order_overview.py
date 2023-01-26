# Copyright (c) 2020-2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import json
from rubirosa.rubirosa.utils import add_items_to_purchase_order, get_sales_order_items
from datetime import datetime

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
        {"label": _("Delivered"), "fieldname": "delivered", "fieldtype": "Percent", "width": 70},
        {"label": _("Purchase Order"), "fieldname": "purchase_order", "fieldtype": "Link", "options": "Purchase Order", "width": 100},
        {"label": _("Check"), "fieldname": "check", "fieldtype": "Data", "width": 100},
        {"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 100},
        {"label": _("Net total"), "fieldname": "base_net_total", "fieldtype": "Currency", "width": 100},
        {"label": _("Currency"), "fieldname": "currency", "fieldtype": "Data", "width": 50},
        {"label": _("Net total"), "fieldname": "net_total", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("Freight"), "fieldname": "freight", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("Commission Base"), "fieldname": "commission_base", "fieldtype": "Float", "precision": 2, "width": 80},
        {"label": _("Sales Partner"), "fieldname": "sales_partner", "fieldtype": "Link", "options": "Sales Partner", "width": 100},
        {"label": _("Commission Rate"), "fieldname": "commission_rate", "fieldtype": "Percent", "width": 50},
        {"label": _("Commission"), "fieldname": "commission", "fieldtype": "Float", "precision": 2, "width": 80}
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
                     `tabSales Order`.`per_delivered` AS `delivered`,
                     SUM(`tabSales Order Item`.`qty`) AS `qty`,
                     SUM(`tabSales Order Item`.`base_net_amount`) AS `order_amount`,
                     (SELECT `tabPurchase Order Item`.`parent`
                      FROM `tabPurchase Order Item`
                      WHERE `tabPurchase Order Item`.`sales_order_trace` LIKE CONCAT("%", `tabSales Order`.`name`, "%")
                        AND `tabPurchase Order Item`.`docstatus` < 2
                      LIMIT 1) AS `purchase_order`,
                     (SELECT IF(IFNULL(`tabSales Order`.`total_qty`, 0) <= IFNULL(SUM(`tabPurchase Order Item`.`qty`), 0), "<span style='color:green; '>OK</span>", "<b><span style='color:red; '>NOK</span></b>")
                      FROM `tabPurchase Order Item`
                      WHERE `tabPurchase Order Item`.`sales_order_trace` LIKE CONCAT("%", `tabSales Order`.`name`, "%")
                        AND `tabPurchase Order Item`.`docstatus` < 2
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
                      AND (`tabCustomer`.`customer_group` LIKE "%Retail%" AND `tabCustomer`.`customer_group` NOT LIKE "%inaktiv%")
                      AND `tabCustomer`.`disabled` = 0
                      {conditions}
                   ) AS `raw`     
                   LEFT JOIN `tabAddress` ON `tabAddress`.`name` = `raw`.`address`
                   LEFT JOIN `tabSales Order` ON `tabSales Order`.`customer` = `raw`.`name`
                                             AND `tabSales Order`.`sales_season` = "{season}"
                                             AND `tabSales Order`.`docstatus` < 2
                   LEFT JOIN `tabSales Order Item` ON `tabSales Order Item`.`parent` = `tabSales Order`.`name`
                   WHERE 
                       (`tabSales Order Item`.`item_code` IS NULL 
                        OR `tabSales Order Item`.`item_code` NOT LIKE "%shipping%")
                   GROUP BY `tabSales Order`.`name`
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
    
    # find sales invoices and commissions
    output = []
    for row in data:
        output.append(row)
        if row['sales_order']:
            sales_invoices = get_sinv_for_so(row['sales_order'])
            first_row = True
            for sales_invoice in sales_invoices:
                if first_row:
                    first_row = False
                else:
                    output.append({})
                output[-1]['sales_invoice'] = sales_invoice['sales_invoice']
                output[-1]['base_net_total'] = sales_invoice['base_net_total']
                output[-1]['currency'] = sales_invoice['currency']
                output[-1]['net_total'] = sales_invoice['net_total']
                output[-1]['freight'] = sales_invoice['freight']
                output[-1]['commission_base'] = sales_invoice['net_total'] - sales_invoice['freight']
                output[-1]['sales_partner'] = sales_invoice['sales_partner']
                output[-1]['commission_rate'] = sales_invoice['commission_rate']
                output[-1]['commission'] = (sales_invoice['commission_rate'] / 100) * (sales_invoice['net_total'] - sales_invoice['freight'])
        
    return output

def get_sinv_for_so(sales_order):
    sql_query = """SELECT 
          `tabSales Invoice Item`.`parent` AS `sales_invoice`, 
          `tabSales Invoice Item`.`sales_order` AS `sales_order`,
          `tabSales Invoice`.`sales_partner` AS `sales_partner`,
          IFNULL(`tabSales Invoice`.`base_net_total`, 0) AS `base_net_total`,
          IFNULL(`tabSales Invoice`.`net_total`, 0) AS `net_total`,
          IFNULL(`tabSales Invoice`.`commission_rate`, 0) AS `commission_rate`,
          `tabSales Invoice`.`currency` AS `currency`,
          IFNULL((SELECT SUM(`amount`)
           FROM `tabSales Invoice Item` AS `tabFreight`
           WHERE `tabFreight`.`parent` = `tabSales Invoice`.`name`
             AND (`tabFreight`.`item_name` LIKE "%Fracht%"
              OR `tabFreight`.`item_name` LIKE "%Shipping%")
          ), 0) AS `freight`
        FROM `tabSales Invoice Item` 
        LEFT JOIN `tabSales Invoice` ON `tabSales Invoice Item`.`parent` = `tabSales Invoice`.`name`
        WHERE `tabSales Invoice`.`docstatus` = 1
          AND `tabSales Invoice Item`.`sales_order` = "{sales_order}"
        GROUP BY `tabSales Invoice`.`name`""".format(sales_order=sales_order)
        
    data = frappe.db.sql(sql_query, as_dict=True)
    return data

@frappe.whitelist()
def create_purchase_order(sales_orders, supplier):
    if type(sales_orders) == str:
        sales_orders = json.loads(sales_orders)
    
    if len(sales_orders) > 0:
        # prepare purchase order
        s = frappe.get_doc("Supplier", supplier)
        purchase_order = frappe.get_doc({
            'doctype': "Purchase Order",
            'supplier': supplier,
            'schedule_date': datetime.now(),
            'currency': s.default_currency
        })
        
        # compile items
        po_items = {}
        for sales_order in sales_orders:
            items = get_sales_order_items(sales_order['sales_order'], supplier)
            for item in items:
                item_code = item.get('item_code')
                if item_code in po_items:
                    # add to existing
                    po_items[item_code]['qty'] += item.get('qty')
                    po_items[item_code]['sales_order_trace'] += "," + sales_order['sales_order']
                else:
                    # create new item
                    po_items[item_code] = {
                        'qty': item.get('qty'),
                        'sales_order': sales_order['sales_order'],
                        'sales_order_trace': sales_order['sales_order']
                    }
                
        # add items to purchase order
        for item_code, values in po_items.items():
            purchase_order.append('items', {
                'item_code': item_code,
                'qty': values.get('qty'),
                'sales_order': values.get('sales_order'),
                'sales_order_trace': values.get('sales_order_trace')
            })
        
        # insert po
        if len(po_items) == 0:
            frappe.throw(_("No applicable items found") )
            
        purchase_order.insert()
        frappe.db.commit()
        
        return purchase_order.name
