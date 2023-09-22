# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import codecs
import os
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
		MAX(CASE WHEN `tabItem Variant Attribute`.`attribute` = 'Size' THEN `tabItem Variant Attribute`.`attribute_value` END) AS `size_value`,
		MAX(CASE WHEN `tabItem Variant Attribute`.`attribute` = 'Colour' THEN `tabItem Variant Attribute`.`attribute_value` END) AS `colour_value`,
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
	LEFT JOIN
		(SELECT DISTINCT
			`tabItem Transfered Table`.`item_code`,
			`tabMultisped Transfered Records`.`date`
		 FROM
			`tabMultisped Transfered Records`
		 LEFT JOIN `tabItem Transfered Table` ON `tabMultisped Transfered Records`.`name` = `tabItem Transfered Table`.`parent`
		 ) AS `mtr` ON `tabItem`.`name` = `mtr`.`item_code`
	LEFT JOIN
		`tabStock Ledger Entry` AS `sle` ON `tabItem`.`name` = `sle`.`item_code`
	WHERE
		`tabItem`.`disabled` = 0
		AND `tabItem`.`is_sales_item` = 1
		AND (`tabItem`.`creation` >= '{change_since}' OR `tabItem`.`modified` >= '{change_since}')
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
    items_record = frappe.render_template('rubirosa/templates/xml/multisped_items.html', {'items': items})
    
    # First attemp of trying to do the file transfer
    # ~ file = codecs.open("{path}MasterDataImp{item_code}.xml".format(path=target_path, item_code=trumpf_item_code), "w", "utf-8")
    # ~ file.write(content)
    # ~ file.close()
    
    # Second way of trying to do the file transfer
    # Define the full path to the destination file
    # ~ destination_file = os.path.join(target_path, "items_record.csv")

    # ~ # Write the items_record content to the destination file
    # ~ with codecs.open(destination_file, 'w', 'utf-8') as file:
        # ~ file.write(items_record)

    # update items record table
    update_items_records(items)
 
    return # ~ {"items_record": items_record}
    
def update_items_records(items):
	#I try to do this with only the "Item Transfered Table" and it was throwing error
    mtr = frappe.get_doc({
        'doctype': 'Multisped Transfered Records',
        'items': []
    })

    # Adding each item code to the 'Item Transfered Table'
    for i in items:
        mtr.append('items', {
            'item_code': i['name']
        })

    mtr.insert(ignore_permissions=True)    
    frappe.db.commit()
    mtr_ref = mtr.name
    frappe.log_error("mtr {0}".format(mtr_ref))
    
    return
