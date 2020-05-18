# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# for generic gtin functions, refer to https://github.com/libracore/erpnextswiss

import frappe

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
