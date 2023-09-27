# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import hashlib  
import codecs
import os
from datetime import date

@frappe.whitelist()
def get_items_data():
    sql_query = """
    SELECT
        IF(`mtr`.`item_code` IS NOT NULL, 'U', 'N') AS `item_status`,
        `tabItem`.`name` AS `name`,
        `tabItem`.`name` AS `item_number`,
        `tabItem`.`description` AS `description`,
        `tabItem`.`item_group` AS `group`,
        MAX(IF(`tabItem Variant Attribute`.`attribute` = 'Size', `tabItem Variant Attribute`.`attribute_value`, NULL)) AS `size_value`,
        MAX(IF(`tabItem Variant Attribute`.`attribute` = 'Colour', `tabItem Variant Attribute`.`attribute_value`, NULL)) AS `colour_value`,
        `tabItem`.`barcode` AS `ean_code`,
        `tabItem`.`stock_uom` AS `stock_uom`,
        `uom`.`uom` AS `uom`,
        `uom`.`conversion_factor` AS `kartonmenge`,
        `tabItem`.`weight_per_unit` AS `weight`,
        `tabItem Price`.`price_list_rate` AS `vk`,
        `tabItem`.`country_of_origin` AS `origin`,
        `tabItem`.`customs_tariff_number` AS `tariff`,
        `tabItem Price`.`currency` AS `currency`      
    FROM
        `tabItem`
    LEFT JOIN
        `tabItem Variant Attribute` ON `tabItem Variant Attribute`.`parent` = `tabItem`.`name`
        AND (`tabItem Variant Attribute`.`attribute` = 'Size' OR `tabItem Variant Attribute`.`attribute` = 'Colour')
    LEFT JOIN `tabMultisped Transfer Record` AS `mtr` ON `tabItem`.`name` = `mtr`.`item_code`
    LEFT JOIN `tabStock Ledger Entry` AS `sle` ON `tabItem`.`name` = `sle`.`item_code`
    LEFT JOIN `tabUOM Conversion Detail` AS `uom` ON `tabItem`.`name` = `uom`.`parent`
    LEFT JOIN
        `tabItem Price` ON `tabItem Price`.`item_code` = `tabItem`.`name`
        AND ( `tabItem Price`.`price_list` = '{price_list}')
    WHERE
        `tabItem`.`disabled` = 0
        AND `tabItem`.`is_sales_item` = 1
        AND `tabItem`.`barcode` IS NOT NULL
    GROUP BY
        `tabItem`.`name`
    ORDER BY
        `tabItem`.`creation` DESC;
    """.format(price_list=frappe.get_value("Multisped Settings", "Multisped Settings", "price_list"))
    data = frappe.db.sql(sql_query, as_dict=True)
    
    indices_to_remove = []
    
    for i, row in enumerate(data):
		
        if row['item_number']:
            row['item_number'] = hashlib.md5(row['item_number'].encode('utf-8')).hexdigest()[:20]
            
        if row['weight']:
            row['weight'] = ("{:,.2f}".format(row['weight'] or 0)).replace(".", ",")
            
        if row['vk'] is None:
            frappe.log_error("Item: {0} Item Number: {1} has no price list'Selling RP EUR' ".format(row['name'],row['item_number']))
            indices_to_remove.append(i)
        else:
            row['vk'] = ("{:,.2f}".format(row['vk'] or 0)).replace(".", ",")
    
    # Remove rows where price_list_rate/vk is None
    for index in reversed(indices_to_remove):
        data.pop(index)
    
    return data

@frappe.whitelist()
def generate_items_transfer_file():    
    # fetch data
    items = get_items_data()

    # fetch Multisped Settings and select tagert path
    settings = frappe.get_doc("Multisped Settings")
    target_path = os.path.join(settings.in_folder,"ItemTransfered{date}.csv".format(date=date.today().strftime("%Y%m%d%H%M%S")))

    # create items transfer file   
    item_content = frappe.render_template('rubirosa/templates/xml/multisped_items.html', {'items': items})
    
    # First attemp of trying to do the file transfer
    file = codecs.open(target_path, "w", "utf-8")
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

@frappe.whitelist()
def create_shipping_order():    
    # fetch data
    dns = get_dns_data()

    # fetch Multisped Settings and select tagert path
    settings = frappe.get_doc("Multisped Settings")
    target_path = os.path.join(settings.in_folder,"DNSTransfered{date}.csv".format(date=date.today().strftime("%Y%m%d%H%M%S")))
    
    # create delivery note transfer file   
    dns_content = frappe.render_template('rubirosa/templates/xml/multisped_dns.html', {'dns': dns})
    
    # First attemp of trying to do the file transfer
    file = codecs.open(target_path, "w", "utf-8")
    file.write(dns_content)
    file.close()

    # update delivery note record table
    update_dns_records(dns)
 
    return 

@frappe.whitelist()
def get_dns_data():
    sql_query = """
    SELECT
        `tabDelivery Note`.`name` AS `name`,
        `tabDelivery Note`.`customer` AS `customer`      
    FROM
        `tabDelivery Note`
    LEFT JOIN `tabMultisped Transfer Record` AS `mtr` ON `tabDelivery Note`.`name` = `mtr`.`delivery_note`
    WHERE
        `tabDelivery Note`.`docstatus` = 1
        AND `mtr`.`delivery_note` IS NULL
    GROUP BY
        `tabDelivery Note`.`name`
    ORDER BY
        `tabDelivery Note`.`creation` DESC;
    """
    data = frappe.db.sql(sql_query, as_dict=True)
    
    return data
    
def update_dns_records(dns):
    
    for dn in dns:
        try:
            mtr = frappe.get_doc({
                'doctype': 'Multisped Transfer Record',
                'delivery_note': dn['name']
            })

            mtr.insert(ignore_permissions=True)    
            frappe.db.commit()
            mtr_ref = mtr.name
        except Exception as e:
            frappe.log_error("{0}\n\n{1}".format(e, dn['name']), "Update Delivery Note Records Failed")
    
    return
