# -*- coding: utf-8 -*-
# Copyright (c) 2018-2022, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# Jinja environment functions

import frappe


def get_sales_season_matrix(sales_season, territory=None):
    conditions = ""
    if territory:
        conditions += """ AND `tabSales Order`.`territory` = "{0}" """.format(territory)
    # get all sold quantities, aggregated per item
    sql_query = """SELECT 
        `tabSales Order Item`.`item_code` AS `item_code`,
        `tabSales Order Item`.`item_name` AS `item_name`,
        SUM(`tabSales Order Item`.`qty`) AS `qty`
    FROM `tabSales Order Item`
    LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabSales Order Item`.`parent`
    WHERE `tabSales Order`.`sales_season` = "{sales_season}"
      AND `tabSales Order`.`docstatus` = 1
      {conditions}
    GROUP BY `tabSales Order Item`.`item_code`;""".format(sales_season=sales_season, conditions=conditions)
    sold_items = frappe.db.sql(sql_query, as_dict=True)
    
    # combine items into matrix
    models = []
    for i in sold_items:
        if i['item_name'] not in models:
            models.append(i['item_name'])
    sizes = ["350", "360", "370", "380", "390", "400", "410", "420", "430", "440", "450", "460", "470", "480"]
    
    # build up matrix
    matrix = {}
    for m in models:
        _row = {}
        for s in sizes:
            for i in sold_items:
                if i['item_name'] == m and s in i['item_code']:
                    _row[s] = i['qty']
                    break
        matrix[m] = _row
    
    return {'sizes': sizes, 'matrix': matrix}
