# -*- coding: utf-8 -*-
# Copyright (c) 2018-2024, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# for generic gtin functions, refer to https://github.com/libracore/erpnextswiss

import frappe
import json
from erpnextswiss.erpnextswiss.gtin import add_check_digit
from frappe.utils import cint

prefix_table = [
    {
        'from': 2000,
        'prefix': "764022079"
    },
    {
        'from': 3000,
        'prefix': "764033533"
    }
]

# this function will return the next available shortcode for GTIN
@frappe.whitelist()
def get_next_ean_shortcode():
    try:
        sql_query = """SELECT `ean_code` 
                   FROM `tabItem`
                   WHERE `ean_code` IS NOT NULL
                   ORDER BY `ean_code` DESC
                   LIMIT 1;"""
        last_ean = frappe.db.sql(sql_query, as_dict=True)
        if last_ean:
            return int(last_ean[0]['ean_code']) + 1
        else:
            return 0
    except Exception as err:
        return 0

@frappe.whitelist()
def get_next_ean():
    next_ean = get_next_ean_shortcode()
    prefix = "764022079"                    # fallback for out-of-scope
    for p in prefix_table:
        if cint(next_ean) >= p['from']:
            prefix = p['prefix']
            
    short_code = ("000{0}".format(next_ean))[-3:]
    full_ean = add_check_digit("{0}{1}".format(prefix, short_code))
    return {
        'next_ean': next_ean,
        'short_code': short_code,
        'full_ean': full_ean
    }
    
# create EAN for multiple items
@frappe.whitelist()
def create_bulk_ean(selected):
    items = json.loads(selected)
    for i in items:
        item = frappe.get_doc("Item", i['name'])
        if not item.ean_code:   # skip if item already has an EAN
            ean = get_next_ean()
            item.ean_code = ean['next_ean']
            item.append("barcodes", {
                'barcode_type': "EAN",
                'barcode': ean['full_ean']
            })
            item.barcode = ean['full_ean']
        item.save()
    return
