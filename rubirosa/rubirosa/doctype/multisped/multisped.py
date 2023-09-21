# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Multisped(Document):
    pass

@frappe.whitelist()
def get_items_data(change_since):
    sql_query = """
    SELECT
		IF(`mtr`.`item` IS NOT NULL, 'U', 'N') AS `item_status`,
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
			`tabItem Transfered Table`.`item`,
			`tabMultisped Transfered Records`.`date`
		 FROM
			`tabMultisped Transfered Records`
		 LEFT JOIN `tabItem Transfered Table` ON `tabMultisped Transfered Records`.`name` = `tabItem Transfered Table`.`parent`
		 ) AS `mtr` ON `tabItem`.`name` = `mtr`.`item`
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
    """.format(change_since=change_since)
    data = frappe.db.sql(sql_query, as_dict=True)
    
    return data

@frappe.whitelist()
def generate_items_transfer_file(change_since=None):    
    # fetch data
    items = get_items_data(change_since)
    
    # fetch Multisped Settings and select tagert path
    settings = frappe.get_doc("Multisped Settings")
    target_path = settings.in_folder
    
    # create csv header
    content = make_line("Kennzeichen|Artikelnummer|Bezeichnung 1|Bezeichnung 2|Artikelgruppe 1|Artikelgruppe 2|ABC – Klassifikation|Merkmal 1|Merkmal 2|EAN – Code|Lagereinheit|Verpackungseinheit|Kartonmenge|Volumen|Gewicht|Länge|Breite|Höhe|VK – Preis Netto|Ursprungsland|Zolltarifnummer|Artikelart|MwSt – Schlüssel|Währungskürzel|Auswert 1|Auswert 2|Auswert 3|Auswert 4|Auswert 5|Text 1|Text 2|Text 3|Text 4|Text 5")
    for i in range(0, len(items)):
        content += make_line("{status}|{article}|{description}|{description_two}|{item_group}|{item_group_two}|{abc}|{size}|{colour}|{ean_code}|{stock_uom}|{pack_uom}|{carton_amount}|{volume}|{weight}|{length}|{width}|{height}|{net_price}|{origin}|{tariff}|{article_type}|{vat}|{currency}|{evaluation_one}|{evaluation_two}|{evaluation_three}|{evaluation_four}|{evaluation_five}|{text_one}|{text_two}|{text_three}|{text_four}|{text_five}".format(
            status=items[i]['item_status'],
            article=items[i]['barcode'],
            description=items[i]['description'],
            description_two= "",
            item_group=items[i]['group'],
            item_group_two= "",
            abc= "",
            size=items[i]['size_value'],
            colour=items[i]['colour_value'],
            ean_code=items[i]['ean_code'],
            stock_uom=items[i]['stock_uom'],
            pack_uom= "",
            carton_amount= "",
            volume= "",
            weight=("{:.3f}".format(items[i]['weight'] or 0)).replace(".", ","),
            length= "",
            width= "",
            height= "",
            net_price= "", #items[i]['????'],
            origin=items[i]['origin'],
            tariff=items[i]['tariff'],
            article_type= "",
            vat= "",
            currency= "",
            evaluation_one= "",
            evaluation_two= "",
            evaluation_three= "",
            evaluation_four= "",
            evaluation_five= "",
            text_one= "",
            text_two= "",
            text_three= "",
            text_four= "",
            text_five= "",
        ))
        
    # ~ items_record = frappe.render_template('rubirosa/multisped/item.html', content)
 
    return { 'content': content }

def make_line(line):
    return line + "\r\n"
