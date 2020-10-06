# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# Interface module for MS Direct

import frappe
# import requests module for http interaction with API
import requests 
from requests.auth import HTTPBasicAuth 
import html
import hashlib

# write an item to MS Direct
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
        'description': html.escape(item.description),
        'item_code': html.escape(item.item_code),
        'not_stock_item': 0 if item.is_stock_item else 1,
        'return_location': html.escape(settings.default_return_location),
        'barcode': html.escape(item.barcode or ""),
        'stock_uom': html.escape(item.stock_uom),
        'valuation_rate': html.escape("{0}".format(item.valuation_rate or 0)),
        'vat_code': html.escape(settings.item_vat_code),
        'header': get_header()
    }
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
    # prepare content
    data = {
        'header': get_header(),
        'date': dn.posting_date,
        'name': delivery_note,
        'items': dn.items,
        'rounded_total': dn.rounded_total,
        'currency': html.escape(settings.item_currency),
        'separate_invoice': 0,
        'language': dn.language,
        'customer_name': html.escape(dn.customer_name),
        'customer_code': abs(hash(dn.customer_name)),
        'shipment_method': dn.shipment_method,
        'customer': {
            'address': html.escape(customer_address.address_line1),
            'address_additional': html.escape(customer_address.address_line2) if customer_address.address_line2 else None,
            'city': html.escape(customer_address.city),
            'pincode': html.escape(customer_address.pincode),
            'country_code': get_country_code(customer_address.country)
        },
        'shipment': {
            'address': html.escape(shipping_address.address_line1),
            'address_additional': html.escape(shipping_address.address_line2) if shipping_address.address_line2 else None,
            'city': html.escape(shipping_address.city),
            'pincode': html.escape(shipping_address.pincode),
            'country_code': get_country_code(shipping_address.country)
        }
    }
    # render content
    xml = frappe.render_template('rubirosa/templates/xml/delivery_note.html', data)
    # post request
    response = post_request(xml)    
    # evaluate response
    result = "undefined"
    if """<wn1:resultCode i:type="d:boolean">1</wn1:resultCode>""" in response.text:
        result = "Success"
    elif """<wn1:errorCode i:type="d:string">ERROR</wn1:errorCode>""" in response.text:
        result = "Error"
        
    # add log
    add_log("delivery Note {0} sent to MS Direct".format(delivery_note), request=xml, response=response.text, result=result)
    return
    
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
    for item in po.items:
        item['warehouse_code'] = frappe.get_value("Warehouse", item.warehouse, "warehouse_code")
        item['barcode'] = frappe.get_value("Item", item.item_code, "barcode")
    # prepare content
    data = {
        'header': get_header(),
        'date': dn.posting_date,
        'name': purchase_order,
        'currency': html.escape(settings.item_currency),
        'email_id': po.contact_email,
        'language': dn.language,
        'supplier_name': html.escape(po.supplier_name),
        'tax_id': frappe.get_value("Supplier", po.supplier, "tax_id"),
        'items': po.items,
        'address': {
            'address': html.escape(shipping_address.address_line1),
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
    return
    
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
def post_request(content):
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    # prepare connection
    auth = HTTPBasicAuth(settings.user, settings.password)
    url = settings.endpoint
    # send request
    response = requests.post(url=url, auth=auth, data=content)
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
