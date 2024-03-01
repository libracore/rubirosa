import frappe
from frappe import _
from rubirosa.rubirosa.utils import get_gps_coordinates
from frappe.modules.utils import sync_customizations

def execute():
    sync_customizations("rubirosa")
    print("Update Coordinates")
    loop = 1
    addresses = frappe.get_all("Address", fields=['name'])
    total = len(addresses)
    for a in addresses:
        print("{0} von {1}".format(loop, total))
        try:
            address = frappe.get_doc("Address", a['name'])
            coordinates = get_gps_coordinates(address, "patch")
            address.save()
            frappe.db.commit()
        except Exception as err:
            print("{0}: {1}".format(a['name'], err))
        loop += 1
    return
    
