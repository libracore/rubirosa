# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)

    return columns, data
    
def get_columns():
    return [
        {"label": _("in CHF"), "fieldname": "label", "fieldtype": "Data", "width": 200},
        {"label": _("Jan"), "fieldname": "jan", "fieldtype": "Currency", "width": 100},
        {"label": _("Feb"), "fieldname": "feb", "fieldtype": "Currency", "width": 100},
        {"label": _("Mar"), "fieldname": "mar", "fieldtype": "Currency", "width": 100},
        {"label": _("Apr"), "fieldname": "apr", "fieldtype": "Currency", "width": 100},
        {"label": _("Mai"), "fieldname": "may", "fieldtype": "Currency", "width": 100},
        {"label": _("Jun"), "fieldname": "jun", "fieldtype": "Currency", "width": 100},
        {"label": _("Jul"), "fieldname": "jul", "fieldtype": "Currency", "width": 100},
        {"label": _("Aug"), "fieldname": "aug", "fieldtype": "Currency", "width": 100},
        {"label": _("Sep"), "fieldname": "sep", "fieldtype": "Currency", "width": 100},
        {"label": _("Okt"), "fieldname": "oct", "fieldtype": "Currency", "width": 100},
        {"label": _("Nov"), "fieldname": "nov", "fieldtype": "Currency", "width": 100},
        {"label": _("Dez"), "fieldname": "dec", "fieldtype": "Currency", "width": 100}
    ]
    
def get_data(filters):
    sql_query = """SELECT
             "Debitoreneingänge (1023, 1024)" AS `label`, 
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-01-01" 
                AND `posting_date` <= "{year}-01-31"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `jan`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-02-01" 
                AND `posting_date` < "{year}-03-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `feb`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-03-01" 
                AND `posting_date` <= "{year}-03-31"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `mar`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-04-01" 
                AND `posting_date` < "{year}-05-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `apr`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-05-01" 
                AND `posting_date` <= "{year}-05-31"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `may`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-06-01" 
                AND `posting_date` < "{year}-07-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `jun`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-07-01" 
                AND `posting_date` < "{year}-08-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `jul`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-08-01" 
                AND `posting_date` < "{year}-09-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `aug`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-09-01" 
                AND `posting_date` < "{year}-10-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `sep`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-10-01" 
                AND `posting_date` < "{year}-11-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `oct`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-11-01" 
                AND `posting_date` < "{year}-12-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `nov`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-12-01" 
                AND `posting_date` <= "{year}-12-31"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `dec`

            UNION SELECT
             "Kreditorenausgänge (1023, 1024)" AS `label`, 
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-01-01" 
                AND `posting_date` <= "{year}-01-31"
                AND (`against` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against_voucher_type` = "Purchase Invoice") AS `jan`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-02-01" 
                AND `posting_date` < "{year}-03-01"
                AND (`against` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against_voucher_type` = "Purchase Invoice") AS `feb`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-03-01" 
                AND `posting_date` <= "{year}-03-31"
                AND (`against` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against_voucher_type` = "Purchase Invoice") AS `mar`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-04-01" 
                AND `posting_date` < "{year}-05-01"
                AND (`against` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against_voucher_type` = "Purchase Invoice") AS `apr`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-05-01" 
                AND `posting_date` <= "{year}-05-31"
                AND (`against` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against_voucher_type` = "Purchase Invoice") AS `may`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-06-01" 
                AND `posting_date` < "{year}-07-01"
                AND (`against` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against_voucher_type` = "Purchase Invoice") AS `jun`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-07-01" 
                AND `posting_date` < "{year}-08-01"
                AND (`against` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against_voucher_type` = "Purchase Invoice") AS `jul`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-08-01" 
                AND `posting_date` < "{year}-09-01"
                AND (`against` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against_voucher_type` = "Purchase Invoice") AS `aug`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-09-01" 
                AND `posting_date` < "{year}-10-01"
                AND (`against` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against_voucher_type` = "Purchase Invoice") AS `sep`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-10-01" 
                AND `posting_date` < "{year}-11-01"
                AND (`against` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against_voucher_type` = "Purchase Invoice") AS `oct`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-11-01" 
                AND `posting_date` < "{year}-12-01"
                AND (`against` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against_voucher_type` = "Purchase Invoice") AS `nov`,
             (SELECT SUM(`debit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-12-01" 
                AND `posting_date` <= "{year}-12-31"
                AND (`against` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against_voucher_type` = "Purchase Invoice") AS `dec`
            
            UNION SELECT
             "Ausgänge Shoeproducers, Raw Material (1023, 1024)" AS `label`, 
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-01-01" 
                AND `posting_date` <= "{year}-01-31"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against` IN (SELECT `name` FROM `tabSupplier` WHERE `supplier_group` IN ("Shoeproducers", "Raw Material"))) AS `jan`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-02-01" 
                AND `posting_date` < "{year}-03-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against` IN (SELECT `name` FROM `tabSupplier` WHERE `supplier_group` IN ("Shoeproducers", "Raw Material"))) AS `feb`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-03-01" 
                AND `posting_date` <= "{year}-03-31"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against` IN (SELECT `name` FROM `tabSupplier` WHERE `supplier_group` IN ("Shoeproducers", "Raw Material"))) AS `mar`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-04-01" 
                AND `posting_date` < "{year}-05-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against` IN (SELECT `name` FROM `tabSupplier` WHERE `supplier_group` IN ("Shoeproducers", "Raw Material"))) AS `apr`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-05-01" 
                AND `posting_date` <= "{year}-05-31"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against` IN (SELECT `name` FROM `tabSupplier` WHERE `supplier_group` IN ("Shoeproducers", "Raw Material"))) AS `may`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-06-01" 
                AND `posting_date` < "{year}-07-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against` IN (SELECT `name` FROM `tabSupplier` WHERE `supplier_group` IN ("Shoeproducers", "Raw Material"))) AS `jun`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-07-01" 
                AND `posting_date` < "{year}-08-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against` IN (SELECT `name` FROM `tabSupplier` WHERE `supplier_group` IN ("Shoeproducers", "Raw Material"))) AS `jul`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-08-01" 
                AND `posting_date` < "{year}-09-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against` IN (SELECT `name` FROM `tabSupplier` WHERE `supplier_group` IN ("Shoeproducers", "Raw Material"))) AS `aug`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-09-01" 
                AND `posting_date` < "{year}-10-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against` IN (SELECT `name` FROM `tabSupplier` WHERE `supplier_group` IN ("Shoeproducers", "Raw Material"))) AS `sep`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-10-01" 
                AND `posting_date` < "{year}-11-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against` IN (SELECT `name` FROM `tabSupplier` WHERE `supplier_group` IN ("Shoeproducers", "Raw Material"))) AS `oct`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-11-01" 
                AND `posting_date` < "{year}-12-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against` IN (SELECT `name` FROM `tabSupplier` WHERE `supplier_group` IN ("Shoeproducers", "Raw Material"))) AS `nov`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-12-01" 
                AND `posting_date` <= "{year}-12-31"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")
                AND `against` IN (SELECT `name` FROM `tabSupplier` WHERE `supplier_group` IN ("Shoeproducers", "Raw Material"))) AS `dec`
                
            UNION SELECT
             "Ausgänge gesamt (1023, 1024)" AS `label`, 
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-01-01" 
                AND `posting_date` <= "{year}-01-31"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `jan`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-02-01" 
                AND `posting_date` < "{year}-03-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `feb`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-03-01" 
                AND `posting_date` <= "{year}-03-31"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `mar`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-04-01" 
                AND `posting_date` < "{year}-05-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `apr`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-05-01" 
                AND `posting_date` <= "{year}-05-31"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `may`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-06-01" 
                AND `posting_date` < "{year}-07-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `jun`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-07-01" 
                AND `posting_date` < "{year}-08-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `jul`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-08-01" 
                AND `posting_date` < "{year}-09-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `aug`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-09-01" 
                AND `posting_date` < "{year}-10-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `sep`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-10-01" 
                AND `posting_date` < "{year}-11-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `oct`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-11-01" 
                AND `posting_date` < "{year}-12-01"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `nov`,
             (SELECT SUM(`credit`) 
              FROM `tabGL Entry`
              WHERE `posting_date` >= "{year}-12-01" 
                AND `posting_date` <= "{year}-12-31"
                AND (`account` LIKE "1023%%" OR `account` LIKE "1024%%")) AS `dec`
      """.format(year=filters.year)

    data = frappe.db.sql(sql_query, as_dict=1)

    # add differential amount as row
    data.append({
        'label': 'Differenz',
        'jan': (data[0]['jan'] or 0) - (data[2]['jan'] or 0),
        'feb': (data[0]['feb'] or 0) - (data[2]['feb'] or 0),
        'mar': (data[0]['mar'] or 0) - (data[2]['mar'] or 0),
        'apr': (data[0]['apr'] or 0) - (data[2]['apr'] or 0),
        'may': (data[0]['may'] or 0) - (data[2]['may'] or 0),
        'jun': (data[0]['jun'] or 0) - (data[2]['jun'] or 0),
        'jul': (data[0]['jul'] or 0) - (data[2]['jul'] or 0),
        'aug': (data[0]['aug'] or 0) - (data[2]['aug'] or 0),
        'sep': (data[0]['sep'] or 0) - (data[2]['sep'] or 0),
        'oct': (data[0]['oct'] or 0) - (data[2]['oct'] or 0),
        'nov': (data[0]['nov'] or 0) - (data[2]['nov'] or 0),
        'dec': (data[0]['dec'] or 0) - (data[2]['dec'] or 0)
    })
    
    return data
