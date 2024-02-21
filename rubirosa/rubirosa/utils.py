# Copyright (c) 2019-2021, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime
from frappe.utils.background_jobs import enqueue
import requests
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

@frappe.whitelist()
def enqueue_add_items_to_purchase_order(sales_order):
    # enqueue adding purchase order items (potential long worker)
    kwargs = {
        'sales_order': sales_order
    }
    
    enqueue('rubirosa.rubirosa.utils.add_items_to_purchase_order', 
        queue='long',
        timeout=15000,
        **kwargs)
    return
    
@frappe.whitelist()
def add_items_to_purchase_order(sales_order):
    so = frappe.get_doc("Sales Order", sales_order)
    log = ""
    for i in so.items:
        if i.supplier:
            supplier = i.supplier
        else:
            item = frappe.get_doc("Item", i.item_code)
            if item.item_defaults and len(item.item_defaults) > 0:
                supplier = item.item_defaults[0].default_supplier
        if supplier:
            # check if there is a draft purchase order
            po_drafts = frappe.get_all("Purchase Order",
                filters={'docstatus': 0, 'supplier': supplier},
                fields=['name'])
            if po_drafts and len(po_drafts) > 0:
                # enrich existing po
                po = frappe.get_doc("Purchase Order", po_drafts[0]['name'])
                row = po.append('items', {
                    'item_code': i.item_code,
                    'qty': i.qty,
                    'sales_order_trace': sales_order
                })
                po.save()
                log += "(+){p}: {q}x {i}<br>".format(p=po_drafts[0]['name'], q=i.qty, i=i.item_code)
            else:
                # create a new po
                s = frappe.get_doc("Supplier", supplier)
                new_po = frappe.get_doc({
                    'doctype': 'Purchase Order',
                    'supplier': supplier,
                    'schedule_date': datetime.now(),
                    'currency': s.default_currency
                })
                row = new_po.append('items', {
                    'item_code': i.item_code,
                    'qty': i.qty,
                    'sales_order_trace': sales_order
                })
                new_po.insert()
                log += "(*){p}: {q}x {i}<br>".format(p=new_po.name, q=i.qty, i=i.item_code)
    if log == "":
        log = "No action"
        frappe.log_error("Order items: no suppliers found", "Create orders from sales orders")
    else:
        add_comment(sales_order, log)
    return log

def add_comment(sales_order, text):
    new_comment = frappe.get_doc({
        'doctype': 'Communication',
        'comment_type': "Comment",
        'content': "Ordered:<br>{0}".format(text),
        'reference_doctype': "Sales Order",
        'status': "Linked",
        'reference_name': sales_order
    })
    new_comment.insert()
    return

"""
Get all sales order items to process to purchase order
"""
@frappe.whitelist()
def get_sales_order_items(sales_order, supplier):
    sql_query = """SELECT 
            `tabSales Order Item`.`item_code`, 
            `tabSales Order Item`.`qty`, 
            `tabItem Supplier`.`supplier`
        FROM `tabSales Order Item`
        LEFT JOIN `tabItem Supplier` ON `tabItem Supplier`.`parent` = `tabSales Order Item`.`item_code`
        WHERE `tabSales Order Item`.`parent` = "{sales_order}"
          AND (`tabItem Supplier`.`supplier` IS NULL OR `tabItem Supplier`.`supplier` = "{supplier}")
        ;""".format(sales_order=sales_order, supplier=supplier)
    items = frappe.db.sql(sql_query, as_dict=True)
    return items

"""
Fetch purchase receipt items with ean codes
"""
@frappe.whitelist()
def get_purchase_receipt_items(purchase_receipt):
    content = frappe.db.sql("""
        SELECT 
            `tabPurchase Receipt Item` .`item_code`,
            `tabPurchase Receipt Item` .`item_name`,
            `tabPurchase Receipt Item` .`qty`,
            `tabItem Barcode`.`barcode`
        FROM `tabPurchase Receipt Item` 
        LEFT JOIN `tabItem Barcode` ON 
            `tabPurchase Receipt Item`.`item_code` = `tabItem Barcode`.`parent` 
            AND `tabItem Barcode`.`barcode_type` = "EAN"
        WHERE `tabPurchase Receipt Item`.`parent` = "{prec}";
    """.format(prec=purchase_receipt), as_dict=True)
    return content

"""
Get data for customer map
"""
@frappe.whitelist()
def get_gps_coordinates(doc, event):
    url = "https://nominatim.openstreetmap.org/search?q={street},{location}&format=json&polygon=1&addressdetails=0".format(street=doc.address_line1, location=doc.city)
    response = requests.get(url)
    data = response.json()
    if len(data) > 0:
        doc.gps_latitude = data[0]['lat']
        doc.gps_longitude = data[0]['lon']
    return

@frappe.whitelist()
def get_locations():
    data = {
        'object': "rubirosa",
        'gps_lat': 47.4113807,
        'gps_long': 9.275177907194573
    }
    query = """
        SELECT
            `raw`.`customer_name` AS `customer`,
            `raw`.`customer_group` AS `customer_group`,
            `tabAddress`.`gps_latitude` AS `gps_lat`, 
            `tabAddress`.`gps_longitude` AS `gps_long`
        FROM (
            SELECT 
                `cust`.`name` AS `customer_name`,
                `cust`.`customer_group`,
                (SELECT `tDLA`.`parent` 
                FROM `tabDynamic Link` AS `tDLA`
                LEFT JOIN `tabAddress` AS `tA` ON `tDLA`.`parent` = `tA`.`name`
                WHERE `tDLA`.`link_name` = `cust`.`name`
                AND `tDLA`.`parenttype` = "Address"
                ORDER BY `tA`.`is_primary_address` DESC
                LIMIT 1) AS `address`
            FROM `tabCustomer` AS `cust`
            WHERE
            (`cust`.`customer_group` = 'Retail Customer Men'
            OR `cust`.`customer_group` = 'Retail Customer Women'
            OR `cust`.`customer_group` = 'Retail Customer Women + Men'
            OR `cust`.`customer_group` LIKE '%Potentials%')
            AND `cust`.`disabled` = 0
            AND `customer_name` != 'Test'
        ) AS `raw`
        LEFT JOIN `tabAddress` ON `tabAddress`.`name` = `raw`.`address`
        ;
    """
    data['locations'] = frappe.db.sql(query, as_dict = True)
    #print(data)
    return data
