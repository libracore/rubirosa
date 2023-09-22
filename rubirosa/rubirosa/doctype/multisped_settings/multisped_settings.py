# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import codecs
import os
from datetime import date
from frappe.model.document import Document

class MultispedSettings(Document):
    pass

@frappe.whitelist()
def get_items_data():
    sql_query = """
    SELECT
        IF(`mtr`.`item_code` IS NOT NULL, 'U', 'N') AS `item_status`,
        `tabItem`.`name`,
        `tabItem`.`barcode` AS `barcode`,
        `tabItem`.`description` AS `description`,
        `tabItem`.`item_group` AS `group`,
        MAX(IF(`tabItem Variant Attribute`.`attribute` = 'Size', `tabItem Variant Attribute`.`attribute_value`, NULL)) AS `size_value`,
        MAX(IF(`tabItem Variant Attribute`.`attribute` = 'Colour', `tabItem Variant Attribute`.`attribute_value`, NULL)) AS `colour_value`,
        `tabItem`.`ean_code` AS `ean_code`,
        `tabItem`.`stock_uom` AS `stock_uom`,
        `tabItem`.`weight_per_unit` AS `weight`,
        `tabItem`.`country_of_origin` AS `origin`,
        `tabItem`.`customs_tariff_number` AS `tariff`       
    FROM
        `tabItem`
    LEFT JOIN
        `tabItem Variant Attribute` ON `tabItem Variant Attribute`.`parent` = `tabItem`.`name`
        AND (`tabItem Variant Attribute`.`attribute` = 'Size' OR `tabItem Variant Attribute`.`attribute` = 'Colour')
    LEFT JOIN `tabMultisped Transfer Record` AS `mtr` ON `tabItem`.`name` = `mtr`.`item_code`
    LEFT JOIN
        `tabStock Ledger Entry` AS `sle` ON `tabItem`.`name` = `sle`.`item_code`
    WHERE
        `tabItem`.`disabled` = 0
        AND `tabItem`.`is_sales_item` = 1
        AND `sle`.`actual_qty` > 0
    GROUP BY
        `tabItem`.`name`
    ORDER BY
        `tabItem`.`creation` DESC;
    """
    data = frappe.db.sql(sql_query, as_dict=True)
    
    return data

@frappe.whitelist()
def generate_items_transfer_file():    
    # fetch data
    items = get_items_data()

    # fetch Multisped Settings and select tagert path
    settings = frappe.get_doc("Multisped Settings")
    target_path = settings.in_folder

    # create transfer file   
    item_content = frappe.render_template('rubirosa/templates/xml/multisped_items.html', {'items': items})
    
    # First attemp of trying to do the file transfer
    file = codecs.open("{path}ItemTransferedFITHH{date}.xml".format(path=target_path, date=date.today()), "w", "utf-8")
    file.write(item_content)
    file.close()

    # update items record table
    update_items_records(items)
 
    return 
    
def update_items_records(items):
    
    for i in items:
        try:
            mtr = frappe.get_doc({
                'doctype': 'Multisped Transfer Record',
                'item_code': i['name']
            })

            mtr.insert(ignore_permissions=True)    
            frappe.db.commit()
            mtr_ref = mtr.name
        except Exception as e:
            frappe.log_error("{0}\n\n{1}".format(e, i['name']), "Update Items Records Failed")
    
    return
