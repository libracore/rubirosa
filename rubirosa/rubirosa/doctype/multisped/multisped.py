# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Multisped(Document):
    pass

@frappe.whitelist()
def get_data():
    sql_query = """
    SELECT
        CASE WHEN DATE(`tabItem`.`modified`) = DATE(`tabItem`.`creation`) THEN 'N'
             WHEN DATE(`tabItem`.`modified`) > DATE(`tabItem`.`creation`) THEN 'U'
             ELSE 'Unknown' END AS `item_status`,
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
        `tabItem`.`customs_tariff_number`AS `tariff`
    FROM
        `tabItem`
    LEFT JOIN
        `tabItem Variant Attribute` ON `tabItem Variant Attribute`.`parent` = `tabItem`.`name`
        AND (`tabItem Variant Attribute`.`attribute` = 'Size' OR `tabItem Variant Attribute`.`attribute` = 'Colour')
    GROUP BY
        `tabItem`.`name`
    ORDER BY
        `tabItem`.`creation` DESC;
    """
    data = frappe.db.sql(sql_query, as_dict=True)
    
    return data

@frappe.whitelist()
def generate_transfer_file():    
    # fetch data
    data = get_data()
    
    # create csv header
    content = make_line("Kennzeichen|Artikelnummer|Bezeichnung 1|Bezeichnung 2|Artikelgruppe 1|Artikelgruppe 2|ABC – Klassifikation|Merkmal 1|Merkmal 2|EAN – Code|Lagereinheit|Verpackungseinheit|Kartonmenge|Volumen|Gewicht|Länge|Breite|Höhe|VK – Preis Netto|Ursprungsland|Zolltarifnummer|Artikelart|MwSt – Schlüssel|Währungskürzel|Auswert 1|Auswert 2|Auswert 3|Auswert 4|Auswert 5|Text 1|Text 2|Text 3|Text 4|Text 5")
    for i in range(0, len(data)):
        content += make_line("{status}|{article}|{description}|{description_two}|{item_group}|{item_group_two}|{abc}|{size}|{colour}|{ean_code}|{stock_uom}|{pack_uom}|{carton_amount}|{volume}|{weight}|{length}|{width}|{height}|{net_price}|{origin}|{tariff}|{article_type}|{vat}|{currency}|{evaluation_one}|{evaluation_two}|{evaluation_three}|{evaluation_four}|{evaluation_five}|{text_one}|{text_two}|{text_three}|{text_four}|{text_five}".format(
            status=data[i]['item_status'],
            article=data[i]['barcode'],
            description=data[i]['description'],
            description_two= "",
            item_group=data[i]['group'],
            item_group_two= "",
            abc= "",
            size=data[i]['size_value'],
            colour=data[i]['colour_value'],
            ean_code=data[i]['ean_code'],
            stock_uom=data[i]['stock_uom'],
            pack_uom= "",
            carton_amount= "",
            volume= "",
            weight=("{:.3f}".format(data[i]['weight'] or 0)).replace(".", ","),
            length= "",
            width= "",
            height= "",
            net_price= "", #data[i]['????'],
            origin=data[i]['origin'],
            tariff=data[i]['tariff'],
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
 
    return { 'content': content }

def make_line(line):
    return line + "\r\n"
