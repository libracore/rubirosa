# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# Interface module for MS Direct

import frappe
# import requests module for http interaction with API
import requests 
from requests.auth import HTTPBasicAuth 
import cgi

# write an item to MS Direct
def write_item(item_code):
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    # get item
    item = frappe.get_doc("Item", item_code)
    # prepare content
    data = {
        'blocked': !item.disabled,
        'currency': cgi.escape(settings.item_currency),
        'item_name': cgi.escape(item.item_name),
        'description': cgi.escape(item.description),
        'item_code': cgi.escape(item.item_code),
        'not_stock_item': !item.is_stock_item),
        'return_location': cgi.escape(settings.default_return_location),
        'barcode': cgi.escape(item.barcode),
        'stock_uom': cgi.escape(item.stock_uom),
        'valuation_rate': cgi.escape(item.valuation_rate),
        'vat_code': cgi.escape(settings.item_vat_code),
        'header': get_header()
    }
    # render content
    xml = frappe.render_template('rubirosa/templates/xml/item.html', data)
    # post request
    response = post_request(xml)
    
def write_delivery_note(delivery_note):
    # get settings
    settings = frappe.get_doc("MS Direct Settings")
    # get item
    dn = frappe.get_doc("Delivery Note", delivery_note)
    # prepare content
    data = {
        'blocked': !item.disabled,
        'currency': cgi.escape(settings.item_currency),
        'item_name': cgi.escape(item.item_name),
        'description': cgi.escape(item.description),
        'item_code': cgi.escape(item.item_code),
        'not_stock_item': !item.is_stock_item),
        'return_location': cgi.escape(settings.default_return_location),
        'barcode': cgi.escape(item.barcode),
        'stock_uom': cgi.escape(item.stock_uom),
        'valuation_rate': cgi.escape(item.valuation_rate),
        'vat_code': cgi.escape(settings.item_vat_code),
        'header': get_header()
    }
    # render content
    xml = frappe.render_template('rubirosa/templates/xml/item.html', data)
    # post request
    response = post_request(xml)    
        
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
