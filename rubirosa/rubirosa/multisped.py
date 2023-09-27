# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import hashlib  
import codecs
import os
import pysftp
from datetime import date, datetime
from frappe.utils.password import get_decrypted_password
from frappe.utils import flt
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt

def get_items_data():
    sql_query = """
        SELECT
            IF(`mtr`.`item_code` IS NOT NULL, 'U', 'N') AS `item_status`,
            `tabItem`.`name` AS `name`,
            `tabItem`.`item_code` AS `item_number`,
            `tabItem`.`description` AS `description`,
            `tabItem`.`item_group` AS `group`,
            (SELECT `tA1`.`attribute_value`
             FROM `tabItem Variant Attribute` AS `tA1`
             WHERE `tA1`.`parent` = `tabItem`.`name`
               AND `tA1`.`attribute` = 'Size') AS `size_value`,
            (SELECT `tA2`.`attribute_value`
             FROM `tabItem Variant Attribute` AS `tA2`
             WHERE `tA2`.`parent` = `tabItem`.`name`
               AND `tA2`.`attribute` = 'Colour') AS `colour_value`,
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
        LEFT JOIN `tabMultisped Transfer Record` AS `mtr` ON `tabItem`.`item_code` = `mtr`.`item_code`
        LEFT JOIN `tabUOM Conversion Detail` AS `uom` ON `tabItem`.`name` = `uom`.`parent`
        LEFT JOIN
            `tabItem Price` ON `tabItem Price`.`item_code` = `tabItem`.`item_code`
            AND ( `tabItem Price`.`price_list` = '{price_list}')
        WHERE
            `tabItem`.`disabled` = 0
            AND `tabItem`.`is_sales_item` = 1
            AND `tabItem`.`barcode` IS NOT NULL
        ORDER BY
        `tabItem`.`creation` DESC;
    """.format(price_list=frappe.get_value("Multisped Settings", "Multisped Settings", "price_list"))
    data = frappe.db.sql(sql_query, as_dict=True)
    
    consolidated_items = []
    
    for d in data:
        
        # rewrite item code to multisped item code (20 digits only - hashed)
        d['item_number'] = get_multisped_item_code(d['item_number'], 20)
        
        # convert weight to comma-notation
        d['weight'] = ("{:.2f}".format(d['weight'] or 0)).replace(".", ",")
        
        # check that there is a sales price and rewrite to comma-notation
        if d['vk']:
            d['vk'] = ("{:.2f}".format(d['vk'] or 0)).replace(".", ",")
        else:
            frappe.log_error("Item: {0} Item Number: {1} has no price list'Selling RP EUR' ".format(d['name'], d['item_number']) , "Multisped Item has no price")
    
    return consolidated_items

@frappe.whitelist()
def generate_items_transfer_file(debug=False):    
    # fetch data
    items = get_items_data()

    # fetch Multisped Settings and select tagert path
    settings = frappe.get_doc("Multisped Settings")
    local_file = os.path.join("/tmp","AS{date}{nn:02d}.txt".format(date=date.today().strftime("%y%m%d"), nn=1))

    # create items transfer file   
    item_content = frappe.render_template('rubirosa/templates/xml/multisped_items.html', {'items': items})
    
    # write to file (note: as the file is in ascii, there might be conversion data loss!)
    f = codecs.open(local_file, "w", encoding="ascii", errors="ignore")
    f.write(item_content)
    f.close()

    # push the file to the target system
    write_file(local_file, settings.in_folder)
    
    # update items record table
    mark_records_transmitted(items, 'item_code')
    
    # cleanup (unless in debug mode)
    if not debug:
        os.remove(local_file)
    
    # create log
    create_multisped_log("Items transferred", item_content)
    
    return
    
def get_multisped_item_code(s, length):
    return hashlib.md5(s.encode('utf-8')).hexdigest()[:length]
    
"""
This function will store an item_code to multisped_code lookup table
"""
def create_multisped_code(item_code):
    if not frappe.db.exists("Multisped Item Code", item_code):
        lookup_entry = frappe.get_doc({
            'doctype': "Multisped Item Code",
            'item_code': item_code,
            'multisped_code': get_multisped_item_code(item_code, 20)
        })
        lookup_entry.insert(ignore_permissions=True)
    return

"""
This function return the ERP item_code of a multisped item_code
"""
def find_item_code_from_multisped_code(multisped_code):
    lookup_items = frappe.get_all("Multisped Item Code",
        filters={'multisped_code': multisped_code},
        fields='item_code'
    )
    if len(lookup_items) > 0:
        return lookup_items[0]['item_code']
    else:
        return None
        
def mark_records_transmitted(record, field):
    
    for i in record:
        try:
            mtr = frappe.get_doc({
                'doctype': 'Multisped Transfer Record',
                field: i['name']
            })

            mtr.insert(ignore_permissions=True)    
            frappe.db.commit()
            
            create_multisped_code(item_code)
            
            mtr_ref = mtr.name
        except Exception as e:
            frappe.log_error("{0}\n\n{1}".format(e, i['name']), "Update Records Failed")

    return
    
def create_multisped_log(reference, content):
    try:
        msped_log = frappe.get_doc({
            'doctype': 'Multisped Log',
            'method': reference,
            'datetime': datetime.now(),
            'content': content
        })

        msped_log.insert(ignore_permissions=True) 
        frappe.db.commit()

    except Exception as e:
        frappe.log_error("{0}\n\n{1}".format(e, reference), "Create Multisped Log Failed")
    
    return 

@frappe.whitelist()
def create_shipping_order(debug=False):    
    # fetch data
    dns = get_dns_data()

    # fetch Multisped Settings and select tagert path
    settings = frappe.get_doc("Multisped Settings")
    local_file = os.path.join("/tmp", "AI{date}{nn:02d}.txt".format(date=date.today().strftime("%y%m%d"), nn=1))
    
    # create delivery note transfer file   
    dns_content = frappe.render_template('rubirosa/templates/xml/multisped_dns.html', {'dns': dns})
    
    # create output file (note: ascii encoding, potential data loss)
    f = codecs.open(local_file, "w", encoding="ascii", errors="ignore")
    f.write(dns_content)
    f.close()

    # push the file to the target system
    write_file(local_file, settings.in_folder)
    
    # update delivery note record table
    mark_records_transmitted(dns,'delivery_note')
    
    # cleanup (unless in debug mode)
    if not debug:
        os.remove(local_file)
    
    # create log
    create_multisped_log("Delivery Notes transferred", dns_content)
    return 

@frappe.whitelist()
def get_dns_data():
    sql_query = """
    SELECT
        `tabDelivery Note`.`name` AS `name`,
        `tabDelivery Note`.`customer` AS `customer`,
        `tabDelivery Note`.`customer_address` AS `invoice_address`,
        `shipping_addrs`.`country` AS `elkz`,
        `shipping_addrs`.`pincode` AS `eplz`,
        `shipping_addrs`.`address_line1` AS `estrasse`,
        `shipping_addrs`.`city` AS `eort`,
        `tabContact`.`mobile_no` AS `avistelefon`,
        `tabContact`.`email_id` AS `avisemail`,
        NULL AS `rechnungsname`,
        `billing_addrs`.`country` AS `rlkz`,
        `billing_addrs`.`pincode` AS `rplz`,
        `billing_addrs`.`address_line1` AS `rstrasse`,
        `billing_addrs`.`city` AS `rort`,
        `tabDelivery Note`.`po_date` AS `auftragsdatum`,
        `tabDelivery Note`.`posting_date` AS `lieferdatum`,
        `tabDelivery Note`.`po_no` AS `auftragsnummer`,
        "Order" AS `auftragsart`,
        `tabDelivery Note`.`woocommerce_order_id` AS `auftragskennz`
    FROM
        `tabDelivery Note`
    LEFT JOIN `tabMultisped Transfer Record` AS `mtr` ON `tabDelivery Note`.`name` = `mtr`.`delivery_note`
    LEFT JOIN `tabAddress` AS `shipping_addrs` ON `tabDelivery Note`.`shipping_address_name` = `shipping_addrs`.`name`
    LEFT JOIN `tabAddress` AS `billing_addrs` ON `tabDelivery Note`.`customer_address` = `billing_addrs`.`name`
    LEFT JOIN `tabContact` ON `tabDelivery Note`.`contact_person` = `tabContact`.`name`

    WHERE
        `tabDelivery Note`.`docstatus` = 1
        AND `mtr`.`delivery_note` IS NULL
    ORDER BY
        `tabDelivery Note`.`creation` DESC
    LIMIT 10
    """
    data = frappe.db.sql(sql_query, as_dict=True)
    
    for d in data:
        # shorten invoice address to hash
        if d['invoice_address']:
            d['invoice_address'] = get_multisped_item_code(d['invoice_address'], 10)
    
    return data

def connect_sftp(settings):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = settings.host_keys or None        # keep or None to push None instead of ""  
    
    connection = pysftp.Connection(
            settings.host_name, 
            port=settings.port,
            username=settings.user, 
            password=get_decrypted_password("Multisped Settings", "Multisped Settings", "password", False),
            cnopts=cnopts
        )
    
    return connection
    
"""
This function will write a local file to an sFTP target folder
"""
def write_file(local_file, target_path):
    settings = frappe.get_doc("Multisped Settings", "Multisped Settings")
    
    try:
        with connect_sftp(settings) as sftp:
            with sftp.cd(target_path):          # e.g. "IN"
                sftp.put(local_file)            # upload file
                
    except Exception as err:
        frappe.log_error( err, "Multisped Write File Failed")
        
    return

"""
This function will read the input path, fetch all files and trigger their action
"""
def read_files(target_path):
    settings = frappe.get_doc("Multisped Settings", "Multisped Settings")
    
    try:
        with connect_sftp(settings) as sftp:
            for file_name in sftp.listdir(target_path):
                # fetch the file
                local_file = os.path.join("/tmp", file_name)
                remote_file = os.path.join("TestOUT", file_name)
                sftp.get(remote_file, local_file)
                # remove remote file
                sftp.remove(remote_file)
                # create a log entry
                f = open(local_file, "r")
                content = f.read()
                f.close()
                # TODO: add log
                
                # read and parse local file
                # TODO parse content
                if file_name.startswith("WR"):
                    # purchase order feedback (Wareneingangs-Rückmeldung)
                    parse_purchase_order_feedback(content)
                elif file_name.startswith("AR"):
                    # delivery note feedback (Auftragsrückmeldung)
                    parse_delivery_note_feedback(content)
                elif file_name.startswith("AR"):
                    # stock reconciliation feedback (Bestandsmeldung)
                    parse_stock_reconciliation_feedback(content)
                # remove local file
                os.remove(local_file)
                
    except Exception as err:
        frappe.log_error( err, "Multisped Read Files Failed")
        
    return

"""
This function will parse a file from a purchase order receipt
"""
def parse_purchase_order_feedback(content):
    field_map = {
        "Lieferantennummer": 0,
        "Bestellnummer": 1,
        "Lieferscheinnummer": 2,
        "Lieferdatum": 3,
        "Bestellposition": 4,
        "Artikelnummer": 5,
        "Teilezustand": 6,
        "Merkmal1": 7,
        "Merkmal2": 8,
        "Palettennummer": 9,
        "Menge": 10,
        "ZC": 11,
        "Buchungsschlüssel": 12,
        "Lagereinheit": 13,
        "Chargennummer": 14,
        "Serialnummer": 15,
        "Bemerkung": 16,
        "MHD": 17
    }
    # parse for all received items
    lines = content.split("\r\n")
    received_items = []
    for line in lines:
        fields = line.split("|")
        received_item = {
            'supplier_no': fields[field_map["Lieferantennummer"]],
            'order_no': fields[field_map["Bestellnummer"]],
            'delivery_note': fields[field_map["Lieferscheinnummer"]],
            'delivery_date': datetime.strptime((fields[field_map["Lieferdatum"]]), "%d.%m.%Y") if fields[field_map["Lieferdatum"]] else None,
            'order_details': fields[field_map["Bestellposition"]],
            'item_code': find_item_code_from_multisped_code(fields[field_map["Artikelnummer"]]),
            'item_state': fields[field_map["Teilezustand"]],
            'attribute1': flt((fields[field_map["Merkmal1"]] or "").replace(",", ".")),
            'attribute2': flt((fields[field_map["Merkmal2"]] or "").replace(",", ".")),
            'parcel_no': fields[field_map["Palettennummer"]],
            'qty': flt((fields[field_map["Menge"]] or "").replace(",", ".")),
            'state_code': fields[field_map["ZC"]],
            'order_key': fields[field_map["Buchungsschlüssel"]],
            'uom': fields[field_map["Lagereinheit"]],
            'batch_no': fields[field_map["Chargennummer"]],
            'serial_no': fields[field_map["Serialnummer"]],
            'remarks': fields[field_map["Bemerkung"]],
            'best_before_date': datetime.strptime((fields[field_map["MHD"]]), "%d.%m.%Y") if fields[field_map["MHD"]] else None
        }
        received_items.append(received_item)
        
    # aggregate items by orders
    receipts_by_order = {}
    for item in received_items:
        # add order if not already there
        if item['order_no'] not in receipts_by_order:
            receipts_by_order[item['order_no']] = {}
        # append this item to the order
        if item['item_code'] not in receipts_by_order[item['order_no']]:
            receipts_by_order[item['order_no']][item['item_code']] = item['qty']
        else:
            receipts_by_order[item['order_no']][item['item_code']] += item['qty']
        
    # create purchase receipt based on receipts
    for order, items in receipts_by_order.items():
        # create downstream document
        purchase_receipt_content = make_purchase_receipt(order)
        # compile document
        purchase_receipt = frappe.get_doc(purchase_receipt_content)
        # set items to actually received items
        received_items = []
        for i in purchase_receipt.items:
            if i.item_code in items:
                _item = i
                _item.qty = items[i.item_code]
                received_items.append(received_items)
        # replace with received items
        purchase_receipt.items = received_items
        # insert
        purchase_receipt.insert(ignore_permissions=True)
        #purchase_receipt.submit()          # uncomment when testing is complete
        
    return received_items

def parse_delivery_note_feedback(content):
    field_map = {
        "Code": 0,
        "Submandant": 1,
        "Client-Idnummer": 2,
        "Client-Idnummerkunde": 3,
        "Zone": 4,
        "Auftragsnummer1": 5,
        "Auftragsnummer2": 6,
        "Auftragsnummerintern": 7,
        "DILOS-Frachtnummer": 8,
        "Differenzen": 9,
        "Datum": 10,
        "Gesamtmenge": 11,
        "Summe_Colli": 12,
        "Summe_Gewicht": 13,
        "Spediteur": 14
    }
    lines = content.split("\r\n")
    for line in lines:
        fields = line.split("|")

        # TODO
        
    return
    
def parse_stock_reconciliation_feedback(contant):
    field_map = {
        "Artikelnummer": 0,
        "Farbe": 1,
        "Grösse": 2,
        "Lotnummer": 3,
        "Menge": 4,
        "Zustand": 5,
        "Teilezustand": 6,
        "MHD": 7
    }
    lines = content.split("\r\n")
    stock_levels = []
    for line in lines:
        fields = line.split("|")
        stock_level = {
            'item_code': find_item_code_from_multisped_code(fields[field_map["Artikelnummer"]]),
            'attribute1': fields[field_map["Farbe"]],
            'attribute2': fields[field_map["Grösse"]],
            'batch_no': fields[field_map["Lotnummer"]],
            'qty': flt((fields[field_map["Menge"]] or "").replace(",", ".")),
            'state_code': fields[field_map["Zustand"]],
            'part_state': fields[field_map["Teilezustand"]],
            'best_before_date': datetime.strptime((fields[field_map["MHD"]]), "%d.%m.%Y") if fields[field_map["MHD"]] else None
        }
        stock_levels.append(received_item)
        
    # aggregate items by orders
    level_by_item = {}
    for item in stock_levels:
        # add order if not already there
        if item['item_code'] not in level_by_item:
            level_by_item[item['item_code']] = item['qty']
        else:
            level_by_item[item['item_code']] += item['qty']
        
    # create stock reconciliation
    settings = frappe.get_doc("Multisped Settings", "Multisped Settings") 
    stock_reconciliation = frappe.get_doc({
        'doctype': "Stock Reconciliation",
    })
    for item_code, qty in level_by_item:
        stock_reconciliation.append("items", {
            'item_code': item_code,
            'warehouse': settings.warehouse,
            'qty': qty
        })
        

    # insert
    stock_reconciliation.insert(ignore_permissions=True)
    #stock_reconciliation.submit()          # uncomment when testing is complete
   
    return
