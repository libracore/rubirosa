# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# Interface module for MS Direct

import frappe
import requests     # import requests module for http interaction with API
from requests.auth import HTTPBasicAuth 
import html         # for escaping
import hashlib      # for hashing item codes
from frappe.utils.password import get_decrypted_password
from bs4 import BeautifulSoup   # for xml parsing responses
from frappe import get_print   # for pdf creation
import base64
from frappe.defaults import get_global_default
import time
from frappe.utils import flt, cint

# write an item to MS Direct
@frappe.whitelist()
def write_item(item_code):
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    # get item
    item = frappe.get_doc("Item", item_code)
    # prepare content
    data = {
        'blocked': item.disabled,
        'currency': html.escape(settings.item_currency),
        'item_name': html.escape(item.item_name),
        'description': html.escape(item.item_code),
        'item_code': html.escape(item.barcode or "{0}".format(abs(hash(item.item_code)))),
        'not_stock_item': 0 if item.is_stock_item else 1,
        'return_location': html.escape(settings.default_return_location),
        'barcode': html.escape(item.barcode or ""),
        'stock_uom': html.escape(frappe.get_value("UOM", item.stock_uom, "ms_direct_uom")),
        'valuation_rate': html.escape("{0}".format(item.valuation_rate or 0)),
        'vat_code': html.escape(settings.item_vat_code),
        'header': get_header(),
        'customs_tariff_number': item.customs_tariff_number if item.customs_tariff_number else None,
        'country_of_origin': get_country_code(item.country_of_origin) if item.country_of_origin else None
    }
    # add last purchase rate if available
    if item.last_purchase_rate:
        data['purchase_price'] = item.last_purchase_rate
        data['purchase_price_currency'] = get_global_default('currency')
    # render content
    xml = frappe.render_template('rubirosa/templates/xml/item.html', data)
    # post request
    response = post_request(xml)
    # evaluate response
    result = "undefined"
    if """<wn1:resultCode i:type="d:boolean">1</wn1:resultCode>""" in response.text:
        result = "Success"
    elif """<wn1:errorCode i:type="d:string">ERROR</wn1:errorCode>""" in response.text:
        result = "Error"
    # add log
    add_log("Item {0} sent to MS Direct".format(item_code), request=xml, response=response.text, result=result)
    return

# write delivery note to MS Direct
@frappe.whitelist()
def write_delivery_note(delivery_note):
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    # get delivery note
    dn = frappe.get_doc("Delivery Note", delivery_note)
    if dn.shipping_address_name:
        shipping_address = frappe.get_doc("Address", dn.shipping_address_name)
    else:
        frappe.throw("Shipping address missing in delivery note {0}".format(delivery_note), "MS Direct write_delivery_note")
    if dn.customer_address:
        customer_address = frappe.get_doc("Address", dn.customer_address)
    else:
        customer_address = shipping_address
    # extend item dict
    items = []
    for item in dn.items:
        ms_uom = frappe.get_value("UOM", item.uom, "ms_direct_uom")
        barcode = frappe.get_value("Item", item.item_code, "barcode")
        if barcode and len(barcode) <= 17:          # ignore items with barcodes longer than 17 characters
            items.append({
                'item_name': item.item_name,
                'item_code': html.escape(barcode),
                'rate': item.rate,
                'idx': item.idx,
                'qty': item.qty,
                'uom': ms_uom,
                'barcode': barcode
            })
    # rewrite shipping method (see ./custom/delivery_note.json)
    shipping = "PCH_ECO"  # default is eco
    if dn.shipping_method == "A-Post":
        shipping = "PLI_PRI"
    elif dn.shipping_method == "B-Post":
        shipping = "PLI_ECO"
    elif dn.shipping_method == "Express":
        shipping = "PLI_EXP"
    elif dn.shipping_method == "Kurier":
        shipping = "DHL_EXP"
    elif dn.shipping_method == "DHL":
        shipping = "DHL"
    elif dn.shipping_method == "Post AT":
        shipping = "PAT_STD"
    elif dn.shipping_method == "Post LI":
        shipping = "PLI_ECO"
    elif dn.shipping_method == "Andere":
        shipping = "DUMMY" 
    # prepare content
    data = {
        'header': get_header(),
        'date': dn.posting_date,
        'name': delivery_note,
        'items': items,
        'rounded_total': dn.rounded_total,
        'currency': html.escape(dn.currency),
        'separate_invoice': 0,
        'language': dn.language,
        'customer_name': html.escape(dn.customer_name),
        'customer_code': abs(hash(dn.customer_name)),
        'shipment_method': shipping,
        'customer': {
            'address': html.escape(customer_address.address_line1),
            'address_additional': html.escape(customer_address.address_line2) if customer_address.address_line2 else None,
            'city': html.escape(customer_address.city or ""),
            'pincode': html.escape(customer_address.pincode or ""),
            'country_code': get_country_code(customer_address.country)
        },
        'shipment': {
            'address': html.escape(shipping_address.address_line1),
            'address_additional': html.escape(shipping_address.address_line2) if shipping_address.address_line2 else None,
            'city': html.escape(shipping_address.city or ""),
            'pincode': html.escape(shipping_address.pincode or ""),
            'country_code': get_country_code(shipping_address.country)
        },
        'documents': {
            'invoice_pdf': get_pdf_base64(delivery_note, print_format=settings.sinv_print_format) if settings.sinv_print_format else None,
            'delivery_pdf': get_pdf_base64(delivery_note, print_format=settings.dn_print_format) if settings.dn_print_format else None
        }
    }
    # render content
    xml = frappe.render_template('rubirosa/templates/xml/delivery_note.html', data)
    # post request
    response = post_request(xml)    
    # evaluate response
    if response:
        result = "undefined"
        if """<wn1:resultCode i:type="d:boolean">1</wn1:resultCode>""" in response.text:
            result = "Success"
        elif """<wn1:errorCode i:type="d:string">ERROR</wn1:errorCode>""" in response.text:
            result = "Error"
            
        # add log
        add_log("Delivery Note {0} sent to MS Direct".format(delivery_note), request=xml, response=response.text, result=result)
    return

# write purchase order to MS Direct
@frappe.whitelist()
def write_purchase_order(purchase_order):
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    # get purchase order
    po = frappe.get_doc("Purchase Order", purchase_order)
    if po.supplier_address:
        supplier_address = frappe.get_doc("Address", po.supplier_address)
    else:
        frappe.throw("Supplier address missing in purchase order {0}".format(purchase_order), "MS Direct write_purchase_order")
    # extend warehouse code and barcode
    items = []
    for item in po.items:
        ms_uom = frappe.get_value("UOM", item.uom, "ms_direct_uom")
        barcode = frappe.get_value("Item", item.item_code, "barcode")
        if barcode and len(barcode) <= 17:          # ignore items with barcodes longer than 17 characters
            items.append({
                'item_name': item.item_name,
                'item_code': html.escape(barcode),
                'rate': item.rate,
                'idx': item.idx,
                'schedule_date': item.schedule_date,
                'qty': item.qty,
                'uom': ms_uom,
                'warehouse_code': frappe.get_value("Warehouse", item.warehouse, "warehouse_code") or "LA",
                'barcode': barcode
            })
    # prepare content
    data = {
        'header': get_header(),
        'date': po.transaction_date,
        'name': purchase_order,
        'currency': html.escape(po.currency),
        'email_id': po.contact_email,
        'language': po.language,
        'supplier_name': html.escape(po.supplier_name),
        'tax_id': frappe.get_value("Supplier", po.supplier, "tax_id"),
        'items': items,
        'address': {
            'address': html.escape(supplier_address.address_line1),
            'city': html.escape(supplier_address.city),
            'country_code': get_country_code(supplier_address.country)
        }
    }
    # render content
    xml = frappe.render_template('rubirosa/templates/xml/purchase_order.html', data)
    # post request
    response = post_request(xml)    
    # evaluate response
    result = "undefined"
    if """<wn1:resultCode i:type="d:boolean">1</wn1:resultCode>""" in response.text:
        result = "Success"
    elif """<wn1:errorCode i:type="d:string">ERROR</wn1:errorCode>""" in response.text:
        result = "Error"
    # add log
    add_log("Purchase Order {0} sent to MS Direct".format(purchase_order), request=xml, response=response.text, result=result)
    # update all item records to make sure that the used
    for item in po.items:
        write_item(item.item_code)
        time.sleep(1)           # delay sending items for 1 sec per item to allow the server to process the item
    return

# write purchase receipt to MS Direct
@frappe.whitelist()
def write_purchase_receipt(purchase_receipt):
    # get purchase order
    pr = frappe.get_doc("Purchase Receipt", purchase_receipt)
    if pr.supplier_address:
        supplier_address = frappe.get_doc("Address", pr.supplier_address)
    else:
        frappe.throw("Supplier address missing in purchase receipt {0}".format(purchase_order), "MS Direct write_purchase_receipt")
        
    # update all item records to make sure that the used
    for item in pr.items:
        write_item(item.item_code)
        time.sleep(1)           # delay sending items for 1 sec per item to allow the server to process the item
        
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    
    # extend warehouse code and barcode
    items = []
    for item in pr.items:
        ms_uom = frappe.get_value("UOM", item.uom, "ms_direct_uom")
        barcode = frappe.get_value("Item", item.item_code, "barcode")
        if barcode and len(barcode) <= 17:          # ignore items with barcodes longer than 17 characters
            items.append({
                'item_name': item.item_name,
                'item_code': html.escape(barcode),
                'rate': item.rate,
                'idx': item.idx,
                'schedule_date': item.schedule_date,
                'qty': item.qty,
                'uom': ms_uom,
                'warehouse_code': frappe.get_value("Warehouse", item.warehouse, "warehouse_code") or "LA",
                'barcode': barcode
            })
    # prepare content
    data = {
        'header': get_header(),
        'date': pr.transaction_date,
        'name': purchase_receipt,
        'currency': html.escape(pr.currency),
        'email_id': pr.contact_email,
        'language': pr.language,
        'supplier_name': html.escape(pr.supplier_name),
        'tax_id': frappe.get_value("Supplier", pr.supplier, "tax_id"),
        'items': items,
        'address': {
            'address': html.escape(supplier_address.address_line1),
            'city': html.escape(supplier_address.city),
            'country_code': get_country_code(supplier_address.country)
        }
    }
    # render content
    xml = frappe.render_template('rubirosa/templates/xml/purchase_order.html', data)
    # post request
    response = post_request(xml)    
    # evaluate response
    result = "undefined"
    if """<wn1:resultCode i:type="d:boolean">1</wn1:resultCode>""" in response.text:
        result = "Success"
    elif """<wn1:errorCode i:type="d:string">ERROR</wn1:errorCode>""" in response.text:
        result = "Error"
    # add log
    add_log("Purchase Receipt {0} sent to MS Direct".format(purchase_order), request=xml, response=response.text, result=result)
    
    return
    
# get purchase orders from MS Direct
@frappe.whitelist()
def get_purchase_orders(debug=False):
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    # prepare content
    data = {
        'header': get_header()
    }
    # render content
    xml = frappe.render_template('rubirosa/templates/xml/purchase_receipt.html', data)
    # get request
    response = post_request(xml)
    # parse orders
    result = parse_purchase_orders(response.text)
    # add log (only if there has been new docs)
    if result:
        add_log("Purchase receipts pulled from MS Direct", request=xml, response=response.text, result=result)
    elif debug:
        add_log("No purchase receipts pulled from MS Direct", request=xml, response=response.text, result="Nothing found")
    return
    
def parse_purchase_orders(response):
    # create soup container
    soup = BeautifulSoup(response, 'lxml')
    # prepare purchase receipts
    purchase_receipts = {}
    # find all item transactions
    items = soup.find_all('wn1:purchasereceiptdata')
    for item in items:
        try:
            po = item.find('wn1:purchaseorderno').getText()
        except:
            po = ""
        # create item record
        # find item code from barcode
        barcode = item.find('wn1:itemno').getText()
        item_match = frappe.get_all("Item", filters={'barcode': barcode}, fields=['name'])
        if len(item_match) == 0:
            frappe.throw("Item not found for barcode {0}".format(barcode))
        received_item = {
            'item_code': item_match[0]['name'],
            'qty': float(item.find('wn1:deliveredquantity').getText())
        }
        if po != "":
            po_doc = frappe.get_doc("Purchase Order", po)
            received_item['purchase_order'] = po
            for i in po_doc.items:
                if i.item_code == item_match[0]['name']:
                    received_item['purchase_order_item'] = i.name
                    break
        # check if this po is in the purche receipt keys
        if po not in purchase_receipts:
            purchase_receipts[po] = {}
            purchase_receipts[po]['items'] = []
        purchase_receipts[po]['items'].append(received_item)
        if po != "":
            purchase_receipts[po]['supplier'] = po_doc.supplier
            purchase_receipts[po]['currency'] = po_doc.currency
        else:
            purchase_receipts[po]['supplier'] = None
    # insert purchase receipts
    if len(purchase_receipts) > 0:
        result = "Inserted "
        for key, value in purchase_receipts.items():
            pr_doc = frappe.get_doc({
                'doctype': "Purchase Receipt",
                'supplier': value['supplier'],
                'currency': value['currency'],
                'items': value['items']
            })
            pr_doc.insert()
            pr_doc.submit()
            frappe.db.commit()
            result += pr_doc.name + " "
    else:
        result = None
    return result

# get order state from MS Direct
@frappe.whitelist()
def get_order_state(debug=False):
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    # prepare content
    data = {
        'header': get_header()
    }
    # render content
    xml = frappe.render_template('rubirosa/templates/xml/order_state.html', data)
    # get request
    response = post_request(xml)
    # parse orders
    result = parse_order_state(response.text)
    # add log (only if there has been new docs)
    if result:
        add_log("Order states pulled from MS Direct", request=xml, response=response.text, result=result)
    elif debug:
        add_log("No order states pulled from MS Direct", request=xml, response=response.text, result="Nothing found")

    return
    
def parse_order_state(response):
    # create soup container
    soup = BeautifulSoup(response, 'lxml')
    # find all item transactions
    orders = soup.find_all('wn1:order')
    result = None
    for order in orders:
        try:
            dn = None
            dns = order.find_all('wn1:orderno')
            for d in dns:
                if d.getText():
                    dn = d.getText()
        except:
            dn = None
        try:
            state = None
            states = order.find_all('wn1:orderstate')
            for s in states:
                if s.getText():
                    state = s.getText()
        except:
            state = None
        try:
            tracking_id = None
            tracking_ids = order.find_all('wn1:linetrackandtraceid')
            for t in tracking_ids:
                if t.getText():
                    tracking_id = t.getText()
        except:
            tracking_id = None
        # match delivery note
        if dn:
            try:
                dn_doc = frappe.get_doc("Delivery Note", dn)
                dn_doc.sendungsnummer = tracking_id
                if state == "0":
                    state = "Open"
                elif state == "1":
                    state = "Shipped"
                elif state == "2":
                    state = "Cancelled"
                elif state == "3":
                    state = "Parital Delivery"
                elif state == "4":
                    state = "In Process"
                elif state == "5":
                    state = "Delivery to Store in Process"
                elif state == "6":
                    state = "Delivered to Store"
                elif state == "7":
                    state = "Picked up from Store by Customer"
                elif state == "8":
                    state = "Partial return"
                elif state == "9":
                    state = "Full return"
                dn_doc.shipping_status = state
                dn_doc.save()
                result = "DN updated"
            except Exception as err:
                frappe.log_error("{0}".format(err), "MS direct: DN reading failed")
    return result

# get item stock from MS Direct
@frappe.whitelist()
def get_item_stock(debug=False, stock_reconciliation=None, warehouse=None, create_new=False):
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    # prepare content
    data = {
        'header': get_header()
    }
    # render content
    xml = frappe.render_template('rubirosa/templates/xml/item_stock.html', data)
    # get request
    response = post_request(xml)
    # parse orders
    result = parse_item_stock(response.text)
    # add log (only if there has been new docs)
    if result:
        add_log("Item stock pulled from MS Direct", request=xml, response=response.text, result=html.escape("{0}".format(result))[:140])
    elif debug:
        add_log("No item stock pulled from MS Direct", request=xml, response=response.text, result="Nothing found")
    # items at 0 are not in transfer file: identify
    all_on_stock = frappe.get_all("Bin", 
        filters=[['warehouse', "=", warehouse], ["actual_qty", ">", 0]],
        fields=["item_code"])
    for item in all_on_stock:
        if item['item_code'] not in result:
            result[item['item_code']] = 0
    # insert items in stock reconciliation
    if create_new or stock_reconciliation:
        if create_new:
            # create a new record
            sr = frappe.get_doc({'doctype': "Stock Reconciliation"})
        else:
            sr = frappe.get_doc("Stock Reconciliation", stock_reconciliation)
        sr.items = []
        for key, value in result.items():
            row = sr.append('items', {
                'item_code': key,
                'qty': value,
                'warehouse': warehouse
            })
        if create_new:
            sr.insert()
            result['stock_reconciliation'] = sr.name
        else:
            sr.save()
            result['stock_reconciliation'] = stock_reconciliation
    return result
    
def parse_item_stock(response):
    # create soup container
    soup = BeautifulSoup(response, 'lxml')
    # find all item transactions
    items = soup.find_all('wn1:productstockdata')
    item_stock = {}
    for item in items:
        barcode = item.find('wn1:itemno').getText()
        #sql_query = """SELECT `name`
        #               FROM `tabItem`
        #               WHERE `barcode` = "{0}" AND `disabled` = 0;""".format(barcode.replace("`", "'"))
        #print(sql_query)
        #item_match = frappe.db.sql(sql_query, as_dict=True)
        item_match = frappe.get_all("Item", filters={'barcode': barcode}, fields=['name'])
        if len(item_match) == 0:
            frappe.log_error("Item not found for barcode {0}".format(barcode), "MS Direct item stock issue")
        else:
            qty = float(item.find('wn1:calculatetquantity').getText())
            item_stock[item_match[0]['name']] = qty
        
    return item_stock
    
def get_header():
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    # compile header
    header = {
        'client_id': settings.client_id,
        'client_name': settings.client_name,
        'token': settings.token
    }
    return header

def get_country_code(country):
    return frappe.get_value("Country", country, "code")

# create a post request to the API
def post_request(content, repeat=0):
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    if (cint(settings.disable_ssl_verification) == 1):
        verify = False
    else:
        verify = True
    password = get_decrypted_password("MS Direct Settings", "MS Direct Settings", 'password')
    # prepare connection
    auth = HTTPBasicAuth(settings.user, password)
    url = settings.endpoint
    # send request
    response = None
    try:
        response = requests.post(url=url, auth=auth, data=content.encode('utf-8'), verify=verify, timeout=120)
    except requests.exceptions.Timeout as e:
        print("POST timed out")
        add_log("MS Direct POST Timeout", request=content, response="Timeout", result="")
        # try again
        if repeat < 10:
            repeat += 1
            response = post_request(content, repeat)
        else:
            return None
    return response

# create a get request to the API
def get_request(content):
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    if (cint(settings.disable_ssl_verification) == 1):
        verify = False
    else:
        verify = True
    password = get_decrypted_password("MS Direct Settings", "MS Direct Settings", 'password')
    # prepare connection
    auth = HTTPBasicAuth(settings.user, password)
    url = settings.endpoint
    # send request
    response = requests.get(url=url, auth=auth, data=content.encode('utf-8'), verify=verify)
    return response
    
def add_log(title, request=None, response=None, result="None"):
    log = frappe.get_doc({
        'doctype': "MS Direct Log",
        'title': title,
        'request': request,
        'response': response,
        'result': result
    })
    log.insert()
    frappe.db.commit()
    return

def get_pdf_base64(delivery_note, print_format):
    # get settings
    settings = frappe.get_doc("MS Direct Settings")  
    # generate pdf
    pdf = get_print(doctype="Delivery Note", name=delivery_note, print_format=print_format, as_pdf=True)
    # encode base64
    encoded = base64.b64encode(pdf)
    # return as string b'BHGhju...'
    return str(encoded)

"""
Migration commands

recursively_send_pos(['PO-00115', 'PO-00098'])

"""
def recursively_send_pos(po_list):
    for po in po_list: 
         doc = frappe.get_doc("Purchase Order", po) 
         for item in doc.items: 
             write_item(item.item_code) 
             print("Sent {0}".format(item.item_code)) 
             time.sleep(1)

    for po in po_list:
        write_purchase_order(po)
        print("Sent {0}".format(po))
        time.sleep(1)
        
def write_latest_items():
    settings = frappe.get_doc("MS Direct Settings")  
    if settings.user:
        items = frappe.db.sql("""SELECT `item_code` 
            FROM `tabItem` 
            WHERE `modified` >= DATE_ADD(CURDATE(), INTERVAL -2 DAY)
              AND `disabled` = 0;""", as_dict=True)                                                                                                                                         
        for item in items: 
             write_item(item['item_code']) 
             print("Sent {0}".format(item['item_code'])) 
             time.sleep(2)
    return
