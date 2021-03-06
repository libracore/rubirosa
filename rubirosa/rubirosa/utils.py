# Copyright (c) 2019-2020, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _

"""
   :params:
   item_code_pattern: "CAI%": item_code mask to find items
   price_list: name of target price list
   rate: set this rate
"""
@frappe.whitelist()
def bulk_set_prices(item_code_pattern, price_list, rate):
    # find applicable items
    sql_query = """SELECT `name` 
                   FROM `tabItem`
                   WHERE `tabItem`.`item_code` LIKE '{pattern}' 
                     AND `tabItem`.`disabled` = 0;""".format(pattern=item_code_pattern)
    applicable_items = frappe.db.sql(sql_query, as_dict=True)
    updated_item_prices = []
    # loop through items
    for item in applicable_items:
        # check if item price exists
        item_prices = frappe.get_all("Item Price", filters={'item_code': item['name'], 'price_list': price_list}, fields=['name'])
        if item_prices:
            # update existing price record
            item_price = frappe.get_doc("Item Price", item_prices[0]['name'])
            item_price.price_list_rate = rate
            item_price.save()
            updated_item_prices.append(item_price.name)
        else:
            # create new item price record
            new_item_price = frappe.get_doc({
                'doctype': 'Item Price',
                'item_code': item['name'],
                'price_list': price_list,
                'price_list_rate': rate
            })
            new_record = new_item_price.insert()
            updated_item_prices.append(new_record.name)
    # write changes to database
    frappe.db.commit()
    return updated_item_prices

@frappe.whitelist()
def consolidate_po_items(purchase_order):
    # load source PO
    po = frappe.get_doc("Purchase Order", purchase_order)
    # collect consolidated items
    items = {}
    for i in po.items:
        if not i.item_code in items:
            items[i.item_code] = {
                'qty': i.qty,
                'sales_order_trace': i.sales_order_trace,
                'item_name': i.item_name,
                'schedule_date': i.schedule_date, 
                'description': i.description,
                'stock_uom': i.stock_uom, 
                'uom': i.uom, 
                'conversion_factor': i.conversion_factor, 
                'base_rate': i.base_rate
            }
        else:
            items[i.item_code]['qty'] += i.qty
            if i.sales_order_trace and i.sales_order_trace not in items[i.item_code]['sales_order_trace']:
                items[i.item_code]['sales_order_trace'] += ";{0}".format(i.sales_order_trace)
    # clear po items
    po.items = []
    # add consolidated items
    for i in sorted(items):
        row = po.append('items', {
            'item_code': i,
            'qty': items[i]['qty'],
            'sales_order_trace': items[i]['sales_order_trace'],
            'item_name': items[i]['item_name'],
            'schedule_date': items[i]['schedule_date'],
            'description': items[i]['description'],
            'stock_uom': items[i]['stock_uom'],
            'uom': items[i]['uom'],
            'conversion_factor': items[i]['conversion_factor'],
            'base_rate': items[i]['base_rate'],
            'base_amount': items[i]['base_rate'] * items[i]['qty']
        })
    # save changes
    po.save()
    return

@frappe.whitelist()
def get_payment_days(customer):
    default_days = 10
    sql_query = """SELECT IFNULL(`tabPayment Terms Template Detail`.`credit_days`, {default}) AS `days`
            FROM `tabCustomer`
            LEFT JOIN `tabPayment Terms Template Detail` ON `tabPayment Terms Template Detail`.`parent` = `tabCustomer`.`payment_terms` 
            WHERE `tabCustomer`.`name` = "{customer}";""".format(customer=customer, default=default_days)
    days = frappe.db.sql(sql_query, as_dict=True)
    if len(days) > 0:
        return days[0]['days']
    else:
        return default_days
