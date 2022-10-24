# Copyright (c) 2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import datetime

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    
    return columns, data

def get_columns(filters):
    return [
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 200},
        {"label": "{0}-{1}".format(filters.year - 1, filters.month), "fieldname": "month_last_year", "fieldtype": "Data", "width": 100},
        {"label": "Budget {0}-{1}".format(filters.year, filters.month), "fieldname": "budget_month_this_year", "fieldtype": "Data", "width": 120},
        {"label": "{0}-{1}".format(filters.year, filters.month), "fieldname": "month_this_year", "fieldtype": "Data", "width": 100},
        {"label": "{0}".format(filters.year - 1), "fieldname": "last_year", "fieldtype": "Data", "width": 100},
        {"label": "Budget {0}".format(filters.year), "fieldname": "budget_this_year", "fieldtype": "Data", "width": 120},
        {"label": "{0}".format(filters.year), "fieldname": "this_year", "fieldtype": "Data", "width": 100},
        {"label": "", "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]
    
    
def get_data(filters):
    # prepare data storage
    data = []
    # define header rows
    data.append({
        'description': '<b>Monthly Report Investors</b>'
    })
    data.append({
        'description': ''
    })
    data.append({
        'description': '<b>Key KPIs</b>',
        'month_last_year': "<b>{0}-{1}</b>".format(filters.year - 1, filters.month),
        'budget_month_this_year': "<b>Budget {0}-{1}</b>".format(filters.year, filters.month),
        'month_this_year': "<b>{0}-{1}</b>".format(filters.year, filters.month),
        'last_year': "<b>{0}</b>".format(filters.year - 1),
        'budget_this_year': "<b>Budget {0}</b>".format(filters.year),
        'this_year': "<b>{0}</b>".format(filters.year)
    })
    
    # insert qty values
    data.append({
        'description': 'Total sold sneakers (QTY)',
        'month_last_year': get_qty(filters.year - 1, filters.month, filters.company),
        'budget_month_this_year': get_qty_budget(filters.year, filters.month),
        'month_this_year': get_qty(filters.year, filters.month, filters.company),
        'last_year': get_qty_ytd(filters.year - 1, filters.month, filters.company),
        'budget_this_year': get_qty_budget_ytd(filters.year, filters.month),
        'this_year': get_qty_ytd(filters.year, filters.month, filters.company)
    })
    
    return data

def get_qty(year, month, company):
    qty = frappe.db.sql("""SELECT IFNULL(SUM(`qty`), 0)
        FROM `tabSales Invoice Item` 
        LEFT JOIN `tabSales Invoice` ON `tabSales Invoice`.`name` = `tabSales Invoice Item`.`parent`
        LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabSales Invoice Item`.`item_code`
        WHERE 
            `tabSales Invoice`.`docstatus` = 1
            AND `tabSales Invoice`.`company` = "{company}"
            AND `tabSales Invoice`.`posting_date` LIKE "{year}-{month}%"
            AND `tabItem`.`is_stock_item` = 1;
        """.format(month=month, year=year, company=company))[0][0]
    return qty
    
def get_qty_ytd(year, month, company):
    
    qty = frappe.db.sql("""SELECT IFNULL(SUM(`qty`), 0)
        FROM `tabSales Invoice Item` 
        LEFT JOIN `tabSales Invoice` ON `tabSales Invoice`.`name` = `tabSales Invoice Item`.`parent`
        LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabSales Invoice Item`.`item_code`
        WHERE 
            `tabSales Invoice`.`docstatus` = 1
            AND `tabSales Invoice`.`company` = "{company}"
            AND `tabSales Invoice`.`posting_date` >= "{year}-01-01"
            AND `tabSales Invoice`.`posting_date` <= "{year}-{month}-{last_day}"
            AND `tabItem`.`is_stock_item` = 1;
        """.format(month=month, year=year, company=company, last_day=last_day_of_month(year, month)))[0][0]
    return qty

def get_qty_budget(year, month):
    qty = frappe.db.sql("""SELECT IFNULL(`qty`, 0)
        FROM `tabBudget Qty Item` 
        LEFT JOIN `tabBudget Qty` ON `tabBudget Qty`.`name` = `tabBudget Qty Item`.`parent`
        WHERE 
            `tabBudget Qty`.`year` = "{year}"
            AND `tabBudget Qty Item`.`month` = "{month}"
            AND `tabBudget Qty Item`.`parentfield` = "qtys";
        """.format(month=month, year=year))[0][0]
    return qty

def get_qty_budget_ytd(year, month):
    qty = frappe.db.sql("""SELECT IFNULL(SUM(`qty`), 0)
        FROM `tabBudget Qty Item` 
        LEFT JOIN `tabBudget Qty` ON `tabBudget Qty`.`name` = `tabBudget Qty Item`.`parent`
        WHERE 
            `tabBudget Qty`.`year` = "{year}"
            AND `tabBudget Qty Item`.`month` <= "{month}"
            AND `tabBudget Qty Item`.`parentfield` = "qtys";
        """.format(month=month, year=year))[0][0]
    return qty
    
def last_day_of_month(year, month):
    return (datetime.date(year, (month % 12) + 1, 1) - datetime.timedelta(days=1)).day
    
