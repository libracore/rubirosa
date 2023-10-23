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
import time
from frappe.utils.password import get_decrypted_password
from frappe.utils import flt
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt

carrier_codes = {
    'SwissPost Economy': '012',
    'SwissPost Priority': '013',
    'UPS Standard': '060',
    'UPS Express Saver': '063',
    'DHL national': '10',
    'DHL national + Retourenetikett': '14',
    'DHL international': '410',
    'GLS': '24',
    'GLS + Retourenetikett': '23',
    'GLS Express': '22',
    'Post Österreich': '100',
    'Post Österreich + Retourenetikett': '102',
}

attribute_codes = {
    'attribute_1': "Size",
    'attribute_2': "Colour"
}

currency_codes = {
    "CHF": 3,
    "EUR": 5,
    "DKK": 8,
    "USD": 23,
    "GBP": 24,
    "NOK": 25,
    "SEK": 26
}

def get_items_data():
    last_item_sync = frappe.get_value("Multisped Settings", "Multisped Settings", "last_item_sync")
    if last_item_sync:
        condition = """ AND `tabItem`.`modified` >= "{sync_date}" """.format(sync_date=last_item_sync)
    else:
        condition = ""
        
    sql_query = """
        SELECT
            `tabItem`.`name` AS `name`,
            `tabItem`.`item_code` AS `item_code`,
            `tabItem`.`description` AS `description`,
            `tabItem`.`item_group` AS `item_group`,
            `tabItem`.`barcode` AS `ean_code`,
            `tabItem`.`stock_uom` AS `stock_uom`,
            `tabItem`.`stock_uom` AS `uom`,
            1 AS `kartonmenge`,
            `tabItem`.`weight_per_unit` AS `weight`,
            `tabItem Price`.`price_list_rate` AS `vk`,
            `tabItem`.`country_of_origin` AS `origin`,
            `tabItem`.`customs_tariff_number` AS `tariff`,
            `tabItem Price`.`currency` AS `currency`      
        FROM
            `tabItem`
        LEFT JOIN
            `tabItem Price` ON `tabItem Price`.`item_code` = `tabItem`.`item_code`
            AND ( `tabItem Price`.`price_list` = '{price_list}')
        WHERE
            `tabItem`.`disabled` = 0
            AND `tabItem`.`is_sales_item` = 1
            AND `tabItem`.`barcode` IS NOT NULL
            {condition}
        ORDER BY `tabItem`.`creation` DESC;
    """.format(price_list=frappe.get_value("Multisped Settings", "Multisped Settings", "price_list"),
        condition=condition)
    data = frappe.db.sql(sql_query, as_dict=True)
    
    # update last sync timestamp
    frappe.set_value("Multisped Settings", "Multisped Settings", "last_item_sync", datetime.now())
    
    consolidated_items = []
    
    for d in data:
        # find status
        transmitted_item = frappe.get_all("Multisped Transfer Record", filters={'item_code': d['item_code']}, fields=['name'])
        if len(transmitted_item) > 0:
            d['item_status'] = "U"
        else:
            d['item_status'] = "N"
            
        # rewrite item code to multisped item code (20 digits only - hashed)
        d['item_number'] = get_multisped_item_code(d['item_code'], 20)
        
        # convert weight to comma-notation
        d['weight'] = format_multisped_number(d['weight'])
        
        # origin: country code
        d['origin'] = frappe.get_cached_value("Country", d['origin'], "code")
        
        # attributes
        attributes = get_attributes(d['item_code'])
        try:
            d['attribute_1'] = attributes[attribute_codes['attribute_1']]
            d['attribute_2'] = attributes[attribute_codes['attribute_2']]
        except:
            # attributes not found - skip
            continue
            
        # check that there is a sales price and rewrite to comma-notation
        if d['vk']:
            d['vk'] = format_multisped_number(d['vk'])
        else:
            frappe.log_error("Item: {0} Item Number: {1} has no price list'Selling RP EUR' ".format(d['name'], d['item_number']) , "Multisped Item has no price")
        
        # append to output
        consolidated_items.append(d)
        
    return consolidated_items

@frappe.whitelist()
def generate_items_transfer_file(debug=False):    
    # fetch data
    items = get_items_data()

    # fetch Multisped Settings and select tagert path
    settings = frappe.get_doc("Multisped Settings", "Multisped Settings")
    local_file = os.path.join("/tmp","AS{date}{nn:02d}.txt".format(date=date.today().strftime("%y%m%d"), nn=(get_transfer_file_count() + 1)))

    # create items transfer file   
    item_content = frappe.render_template('rubirosa/templates/xml/multisped_items.html', {'items': items})
    
    # write to file
    f = codecs.open(local_file, "w", encoding="utf-8", errors="ignore")
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
    create_multisped_log("Items transferred {0}".format(local_file.replace("/tmp/", "")), item_content)
    
    return
    
def get_multisped_item_code(s, length):
    return hashlib.md5(s.encode('utf-8')).hexdigest()[:length]

def get_stock_data():
    settings = frappe.get_doc("Multisped Settings", "Multisped Settings")
    sql_query = """
        SELECT
            `tabBin`.`item_code` AS `item_code`,
            `tabBin`.`actual_qty` AS `actual_qty`
        FROM
            `tabBin`
        WHERE
            `tabBin`.`warehouse` = "{warehouse}"
        ;
    """.format(warehouse=settings.warehouse)
    data = frappe.db.sql(sql_query, as_dict=True)
    
    for d in data:            
        # rewrite item code to multisped item code (20 digits only - hashed)
        d['item_number'] = get_multisped_item_code(d['item_code'], 20)
        
        d['actual_qty'] = format_multisped_number(d['actual_qty'])
        
        # attributes
        attributes = get_attributes(d['item_code'])
        try:
            d['attribute_1'] = attributes[attribute_codes['attribute_1']]
            d['attribute_2'] = attributes[attribute_codes['attribute_2']]
        except:
            # attributes not found - skip
            continue
        
    return data
    
@frappe.whitelist()
def generate_stock_transfer_file(debug=False):    
    # fetch data
    stock = get_stock_data()

    # fetch Multisped Settings and select tagert path
    settings = frappe.get_doc("Multisped Settings", "Multisped Settings")
    local_file = os.path.join("/tmp","BE{date}.dat".format(date=date.today().strftime("%Y%m%d")))

    # create items transfer file   
    item_content = frappe.render_template('rubirosa/templates/xml/multisped_stock.html', {'items': stock})
    
    # write to file
    f = codecs.open(local_file, "w", encoding="utf-8", errors="ignore")
    f.write(item_content)
    f.close()

    # push the file to the target system
    write_file(local_file, settings.in_folder)
    
    # cleanup (unless in debug mode)
    if not debug:
        os.remove(local_file)
    
    # create log
    create_multisped_log("Stock transferred {0}".format(local_file.replace("/tmp/", "")), item_content)
    
    return
    
"""
This function will store an item_code to multisped_code lookup table
"""
def store_multisped_code(item_code):
    if not frappe.db.exists("Multisped Item Code", item_code):
        lookup_entry = frappe.get_doc({
            'doctype': "Multisped Item Code",
            'item_code': item_code,
            'multisped_code': get_multisped_item_code(item_code, 20)
        })
        lookup_entry.insert(ignore_permissions=True)
    return

"""
Format a number into the multisped format (comma as decimal separator, no thousands seeparator)
"""
def format_multisped_number(n):
    return ("{:.2f}".format(n or 0)).replace(".", ",")
    
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

"""
Create a transfer record so that the system knows an item or delivery note or purchase order has been transmitted
"""
def mark_records_transmitted(record, field):
    
    for i in record:
        try:
            mtr = frappe.get_doc({
                'doctype': 'Multisped Transfer Record',
                field: i['name']
            })

            mtr.insert(ignore_permissions=True)    
            frappe.db.commit()
            
            if field == "item_code":
                store_multisped_code(i['name'])
            
            mtr_ref = mtr.name
        except Exception as e:
            frappe.log_error("{0}\n\n{1}: {2}".format(e, field, i['name']), "Update Records Failed")

    return

"""
Add a log entry with the file content
"""
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
def generate_shipping_order(debug=False):    
    # fetch data
    dns = get_dns_data()

    # fetch Multisped Settings and select tagert path
    settings = frappe.get_doc("Multisped Settings")
    local_file = os.path.join("/tmp", "AI{date}{nn:02d}.txt".format(date=date.today().strftime("%y%m%d"), nn=(get_transfer_file_count() + 1)))
    
    # create delivery note transfer file   
    dns_content = frappe.render_template('rubirosa/templates/xml/multisped_dns.html', {'dns': dns})
    
    # create output file
    f = codecs.open(local_file, "w", encoding="utf-8", errors="ignore")
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
    create_multisped_log("Delivery Notes transferred {0}".format(local_file.replace("/tmp", "")), dns_content)
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
        IF(`tabContact`.`phone`, `tabContact`.`phone`, `tabContact`.`mobile_no`) AS `avistelefon`,
        `tabContact`.`email_id` AS `avisemail`,
        `billing_addrs`.`country` AS `rlkz`,
        `billing_addrs`.`pincode` AS `rplz`,
        `billing_addrs`.`address_line1` AS `rstrasse`,
        `billing_addrs`.`city` AS `rort`,
        IF(`tabDelivery Note`.`po_date`, `tabDelivery Note`.`po_date`, `tabDelivery Note`.`posting_date`) AS `po_date`,
        `tabDelivery Note`.`posting_date` AS `posting_date`,
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
    """
    data = frappe.db.sql(sql_query, as_dict=True)
    
    for d in data:
        # pull original document
        dn_doc = frappe.get_doc("Delivery Note", d['name'])
        # append items
        d['items'] = dn_doc.as_dict()['items']
        for i in d['items']:
            i['item_number'] = get_multisped_item_code(i['item_code'], 20)
            i['qty'] = format_multisped_number(i['qty'])
            i['rate'] = format_multisped_number(i['rate'])
            i['quantity_ordered'] = format_multisped_number(i['quantity_ordered'])
            # find atttributes
            attributes = get_attributes(i['item_code'])
            i['attribute_1'] = attributes.get(attribute_codes['attribute_1'])
            i['attribute_2'] = attributes.get(attribute_codes['attribute_2'])
            # set currency code
            i['currency_code'] = currency_codes[dn_doc.currency]
            
        # shorten invoice address and customer to hash
        if d['invoice_address']:
            d['invoice_address'] = get_multisped_item_code(d['invoice_address'], 10)
        d['customer_id'] = int(time.mktime((frappe.get_value("Customer", d['customer'], "creation")).timetuple()))
        
        # rewrite country name to country code
        if d['elkz']:
            d['elkz'] = frappe.get_cached_value("Country", d['elkz'], "code")
        if d['rlkz']:
            d['rlkz'] = frappe.get_cached_value("Country", d['rlkz'], "code")
        
        # define carrier
        d['carrier'] = carrier_codes(dn_doc.shipping_method) if dn_doc.shipping_method in carrier_codes else carrier_codes['SwissPost Economy']
        
    return data

def get_attributes(item_code):
    item_doc = frappe.get_doc("Item", item_code)
    attributes = {}
    for a in item_doc.attributes:
        attributes[a.attribute] = a.attribute_value
    return attributes

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
def read_files():
    settings = frappe.get_doc("Multisped Settings", "Multisped Settings")
    target_path = settings.out_folder
    
    if True: #try:
        with connect_sftp(settings) as sftp:
            for file_name in sftp.listdir(target_path):
                # fetch the file
                local_file = os.path.join("/tmp", file_name)
                remote_file = os.path.join(target_path, file_name)
                sftp.get(remote_file, local_file)
                # remove remote file
                sftp.remove(remote_file)
                # create a log entry
                f = open(local_file, "r")
                content = f.read()
                f.close()
                
                # read and parse local file
                # TODO parse content
                if file_name.startswith("WR"):
                    # purchase order feedback (Wareneingangs-Rückmeldung)
                    create_multisped_log("Received purchase receipt {0}".format(file_name), content)
                    parse_purchase_order_feedback(content)
                elif file_name.startswith("AR"):
                    # delivery note feedback (Auftragsrückmeldung)
                    create_multisped_log("Received delivery feedback {0}".format(file_name), content)
                    parse_delivery_note_feedback(content)
                elif file_name.startswith("BE"):
                    # stock reconciliation feedback (Bestandsmeldung)
                    create_multisped_log("Received stock reconciliation {0}".format(file_name), content)
                    parse_stock_reconciliation_feedback(content)
                # remove local file
                os.remove(local_file)
                
    #except Exception as err:
    #    frappe.log_error( err, "Multisped Read Files Failed")
        
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
    lines = content.replace("\r", "").split("\n")
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
    for item in received_items.items():
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
    lines = content.replace("\r", "").split("\n")
    delivery_notes = []
    _delivery_note = None
    for line in lines:
        fields = line.split("|")

        if fields[0] == "K*":
            # this is a head record - new delivery note
            if _delivery_note:
                delivery_notes.append(_delivery_note)
            
            _delivery_note = {
                'subtenant': fields[1],
                'client_id': fields[2],
                'client_customer': fields[3],
                'region': fields[4],
                'delivery_note': fields[5],            # this is the delivery note name
                'order_no_2': fields[6],
                'order_no_internal': fields[7],
                'dilos': fields[8],
                'deviations': fields[9],
                'date': datetime.strptime(fields[10], "%d.%m.%Y"),  # as dd.mm.yyyy
                'total_qty': fields[11],
                'total_colli': fields[12],
                'total_weight': fields[13],
                'carrier': fields[14],
                'items': [],
                'parcels': [],
                'picking': []
            }
        elif fields[0] == "P*":
            # this is a position record
            _delivery_note['items'].append({
                'delivery_note': fields[1],
                'pos': fields[2],
                'item_code': fields[3],
                'state': fields[4],
                'attribute_1': fields[5],
                'attribute_2': fields[6],
                'serial': fields[7],
                'batch': fields[8],
                'qty': fields[9],
                'delivered_qty': fields[10],
                'outstanding_qty': fields[11],
                'best_before_date': fields[12]
            })
        elif fields[0] == "C*":
            # this is a parcel record
            _delivery_note['parcels'].append({
                'delivery_note': fields[1],
                'parcel': fields[2],
                'packaging': fields[3],
                'service': fields[4],
                'weight': fields[5],
                'tracking_return': fields[6]
            })
        elif fields[0] == "L*":
            # this is a packing record
            _delivery_note['picking'].append({
                'delivery_note': fields[1],
                'pos': fields[2],
                'item_code': fields[3],
                'state': fields[4],
                'attribute_1': fields[5],
                'attribute_2': fields[6],
                'serial': fields[7],
                'batch': fields[8],
                'picking_qty': fields[9],
                'package_no': fields[10],
                'best_before_date': fields[11]
            })
    # attach last delivery note
    if _delivery_note:
        delivery_notes.append(_delivery_note)
        
    # update delivery note information
    for dn in delivery_notes:
        dn_doc = frappe.get_doc("Delivery Note", dn['delivery_note'])
        dn_doc.sendungsnummer = dn['parcels'][0]['parcel']
        dn_doc.save()
        
    frappe.db.commit()
    
    return
    
def parse_stock_reconciliation_feedback(content):
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
    lines = content.replace("\r", "").split("\n")
    stock_levels = []
    for line in lines:
        fields = line.split("|")
        if len(fields) >= 8:
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
            stock_levels.append(stock_level)
        
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
    for item_code, qty in level_by_item.items():
        stock_reconciliation.append("items", {
            'item_code': item_code,
            'warehouse': settings.warehouse,
            'qty': qty
        })
        
    # insert
    stock_reconciliation.flags.ignore_validate = True
    stock_reconciliation.insert(ignore_permissions=True)
    #stock_reconciliation.submit()          # uncomment when testing is complete
   
    return

def get_transfer_file_count():
    count = frappe.db.sql("""
        SELECT IFNULL(COUNT(`name`), 0) AS `count`
        FROM `tabMultisped Log`
        WHERE `method` LIKE "%transferred%"
          AND `creation` >= CURDATE();
        """, as_dict=True)[0]['count']
    return count
