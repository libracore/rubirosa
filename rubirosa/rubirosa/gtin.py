# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# for generic gtin functions, refer to https://github.com/libracore/erpnextswiss

import frappe
import json
from erpnextswiss.erpnextswiss.gtin import add_check_digit

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

# create EAN for multiple items
@frappe.whitelist()
def create_bulk_ean(selected, prefix):
    items = json.loads(selected)
    for i in items:
        item = frappe.get_doc("Item", i['name'])
        if not item.ean_code:   # skip if item already has an EAN
            short_code = ("000{0}".format(get_next_ean_shortcode()))[-3:]
            full_ean = add_check_digit("{0}{1}".format(prefix, short_code))
            item.ean_code = short_code
            item.append("barcodes", {
                'barcode_type': "EAN",
                'barcode': full_ean
            })
            item.barcode = full_ean
        item.save()
    return
