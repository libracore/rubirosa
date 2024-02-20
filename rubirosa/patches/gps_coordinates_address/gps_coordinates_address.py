import frappe
from frappe import _
from rubirosa.rubirosa.utils import get_gps_coordinates

def execute():
    frappe.reload_doc("rubirosa", "doctype", "Address")
    print("Update Coordinates")
    loop = 1
    query = """
        SELECT * FROM `tabAddress`
        """
    addresses = frappe.db.sql(query, as_dict=True)
    total = len(addresses)
    for address in addresses:
        print("{0} von {1}".format(loop, total))
        try:
            coordinates = get_gps_coordinates(address, "event")
            frappe.db.set_value("Address", address.name, "gps_latitude", coordinates[0])
            frappe.db.set_value("Address", address.name, "gps_longitude", coordinates[1])
            frappe.db.commit()
        except Exception as err:
            print(err)
        loop += 1
    return
    