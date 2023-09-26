# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# Interface module for Multisped

import frappe
import sftp
from frappe.utils.password import get_decrypted_password
from datetime import datetime
from frappe.utils import flt
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt

def connect_sftp(settings):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = settings.host_keys or None        # keep or None to push None instead of ""  
    
    return pysftp.Connection(
            settings.host_name, 
            port=settings.port,
            username=settings.user, 
            password=get_decrypted_password("Multisped Settings", "Multisped Settings", "password", False),
            cnopts=cnopts
        )
            
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
            'item_code': fields[field_map["Artikelnummer"]],
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
    for order, items in receipts_by_order.items()
        # create downstream document
        purchase_receipt_content = make_purchase_receipt(order)
        # compile document
        purchase_receipt = frappe.get_doc(purchase_receipt_content)
        # set items to actually received items
        received_items = []
        for i in purchase_receipt.items:
            # note: this is the multisped item code -> rewrite to ERPNext (TODO)
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
            'item_code': fields[field_map["Artikelnummer"]],
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
        # note: this is the multisped item code -> rewrite to ERPNext (TODO)
        stock_reconciliation.append("items", {
            'item_code': item_code,
            'warehouse': settings.warehouse,
            'qty': qty
        })
        

    # insert
    stock_reconciliation.insert(ignore_permissions=True)
    #stock_reconciliation.submit()          # uncomment when testing is complete
    
    return
