# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# Interface module for Multisped

import frappe
import sftp
from frappe.utils.password import get_decrypted_password

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
            for obj in sftp.listdir(target_path):
                print(obj)
                
    except Exception as err:
        frappe.log_error( err, "Multisped Read Files Failed")
        
    return
