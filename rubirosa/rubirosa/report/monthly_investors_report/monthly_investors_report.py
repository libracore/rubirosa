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
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 300},
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
    
    data.append({
        'description': 'Therof sold sneakers online (QTY)',
        'month_last_year': get_qty(filters.year - 1, filters.month, filters.company, online=True),
        'budget_month_this_year': get_qty_budget(filters.year, filters.month, online=True),
        'month_this_year': get_qty(filters.year, filters.month, filters.company, online=True),
        'last_year': get_qty_ytd(filters.year - 1, filters.month, filters.company, online=True),
        'budget_this_year': get_qty_budget_ytd(filters.year, filters.month, online=True),
        'this_year': get_qty_ytd(filters.year, filters.month, filters.company, online=True)
    })
    data.append({
        'description': ''
    })
    
    # revenue KPIs
    accounts = ["3400", "3401", "3402", "3403", "3404", "3405"]
    data.append({
        'description': 'Gross Revenue (CHF) (3400-3405)',
        'month_last_year': "{:,.2f}".format(get_turnover(filters.year - 1, filters.month, accounts, filters.company)).replace(",", "'"),
        'budget_month_this_year': "{:,.2f}".format(get_turnover_budget(filters.year, filters.month, accounts, filters.company)).replace(",", "'"),
        'month_this_year': "{:,.2f}".format(get_turnover(filters.year, filters.month, accounts, filters.company)).replace(",", "'"),
        'last_year': "{:,.2f}".format(get_turnover_ytd(filters.year - 1, filters.month, accounts, filters.company)).replace(",", "'"),
        'budget_this_year': "{:,.2f}".format(get_turnover_budget_ytd(filters.year, filters.month, accounts, filters.company)).replace(",", "'"),
        'this_year': "{:,.2f}".format(get_turnover_ytd(filters.year, filters.month, accounts, filters.company)).replace(",", "'")
    })
    
    accounts = ["3410"]
    data.append({
        'description': '-Commission Agents (CHF) (3410)',
        'month_last_year': "{:,.2f}".format(get_turnover(filters.year - 1, filters.month, accounts, filters.company)).replace(",", "'"),
        'budget_month_this_year': "{:,.2f}".format(get_turnover_budget(filters.year, filters.month, accounts, filters.company)).replace(",", "'"),
        'month_this_year': "{:,.2f}".format(get_turnover(filters.year, filters.month, accounts, filters.company)).replace(",", "'"),
        'last_year': "{:,.2f}".format(get_turnover_ytd(filters.year - 1, filters.month, accounts, filters.company)).replace(",", "'"),
        'budget_this_year': "{:,.2f}".format(get_turnover_budget_ytd(filters.year, filters.month, accounts, filters.company)).replace(",", "'"),
        'this_year': "{:,.2f}".format(get_turnover_ytd(filters.year, filters.month, accounts, filters.company)).replace(",", "'")
    })
    
    accounts = ["3408", "3480", "3490"]
    data.append({
        'description': '-Factoring / Skonto (CHF) (3408, 3480, 3490)',
        'month_last_year': "{:,.2f}".format(get_turnover(filters.year - 1, filters.month, accounts, filters.company)).replace(",", "'"),
        'budget_month_this_year': "{:,.2f}".format(get_turnover_budget(filters.year, filters.month, accounts, filters.company)).replace(",", "'"),
        'month_this_year': "{:,.2f}".format(get_turnover(filters.year, filters.month, accounts, filters.company)).replace(",", "'"),
        'last_year': "{:,.2f}".format(get_turnover_ytd(filters.year - 1, filters.month, accounts, filters.company)).replace(",", "'"),
        'budget_this_year': "{:,.2f}".format(get_turnover_budget_ytd(filters.year, filters.month, accounts, filters.company)).replace(",", "'"),
        'this_year': "{:,.2f}".format(get_turnover_ytd(filters.year, filters.month, accounts, filters.company)).replace(",", "'")
    })
    
    # growing rate revenue
    net_revenue_month = get_float(data[-3]['month_this_year']) + get_float(data[-2]['month_this_year']) + get_float(data[-1]['month_this_year'])
    avg_revenue_year = (get_float(data[-3]['this_year']) + get_float(data[-2]['this_year']) + get_float(data[-1]['this_year'])) / filters.month
    budget_month = get_float(data[-3]['budget_month_this_year']) + get_float(data[-2]['budget_month_this_year']) + get_float(data[-1]['budget_month_this_year'])
    avg_budget_year = (get_float(data[-3]['budget_this_year']) + get_float(data[-2]['budget_this_year']) + get_float(data[-1]['budget_this_year']))
    data.append({
        'description': 'Growing Rate Gross Revenue',
        'month_last_year': "",
        'budget_month_this_year': "{:,.2f}%".format(100 * budget_month / avg_budget_year).replace(",", "'"),
        'month_this_year': "{:,.2f}%".format(100 * net_revenue_month / avg_revenue_year).replace(",", "'"),
        'last_year': "",
        'budget_this_year': "",
        'this_year': ""
    })
    
    return data

def get_float(s):
    return float(s.replace("'", ""))
    
def get_qty(year, month, company, online=False):
    condition = """ AND `tabSales Invoice`.`customer_group` LIKE "%Online%" """ if online else ""
    
    qty = frappe.db.sql("""SELECT IFNULL(SUM(`qty`), 0)
        FROM `tabSales Invoice Item` 
        LEFT JOIN `tabSales Invoice` ON `tabSales Invoice`.`name` = `tabSales Invoice Item`.`parent`
        LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabSales Invoice Item`.`item_code`
        WHERE 
            `tabSales Invoice`.`docstatus` = 1
            AND `tabSales Invoice`.`company` = "{company}"
            AND `tabSales Invoice`.`posting_date` LIKE "{year}-{month:02d}%"
            AND `tabItem`.`is_stock_item` = 1
            {condition};
        """.format(month=month, year=year, company=company, condition=condition))[0][0]
    return qty
    
def get_qty_ytd(year, month, company, online=False):
    condition = """ AND `tabSales Invoice`.`customer_group` LIKE "%Online%" """ if online else ""
    
    qty = frappe.db.sql("""SELECT IFNULL(SUM(`qty`), 0)
        FROM `tabSales Invoice Item` 
        LEFT JOIN `tabSales Invoice` ON `tabSales Invoice`.`name` = `tabSales Invoice Item`.`parent`
        LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabSales Invoice Item`.`item_code`
        WHERE 
            `tabSales Invoice`.`docstatus` = 1
            AND `tabSales Invoice`.`company` = "{company}"
            AND `tabSales Invoice`.`posting_date` >= "{year}-01-01"
            AND `tabSales Invoice`.`posting_date` <= "{year}-{month:02d}-{last_day}"
            AND `tabItem`.`is_stock_item` = 1
            {condition};
        """.format(month=month, year=year, company=company, last_day=last_day_of_month(year, month),
            condition=condition))[0][0]
    return qty

def get_qty_budget(year, month, online=False):
    target = "qtys_online" if online else "qtys"
    
    try:
        qty = frappe.db.sql("""SELECT IFNULL(`qty`, 0)
            FROM `tabBudget Qty Item` 
            LEFT JOIN `tabBudget Qty` ON `tabBudget Qty`.`name` = `tabBudget Qty Item`.`parent`
            WHERE 
                `tabBudget Qty`.`year` = "{year}"
                AND `tabBudget Qty Item`.`month` = "{month}"
                AND `tabBudget Qty Item`.`parentfield` = "{target}";
            """.format(month=month, year=year, target=target))[0][0]
    except:
        return 0
    return qty

def get_qty_budget_ytd(year, month, online=False):
    target = "online_qtys" if online else "qtys"
    
    try:
        qty = frappe.db.sql("""SELECT IFNULL(SUM(`qty`), 0)
            FROM `tabBudget Qty Item` 
            LEFT JOIN `tabBudget Qty` ON `tabBudget Qty`.`name` = `tabBudget Qty Item`.`parent`
            WHERE 
                `tabBudget Qty`.`year` = "{year}"
                AND `tabBudget Qty Item`.`month` <= "{month}"
                AND `tabBudget Qty Item`.`parentfield` = "{target}";
            """.format(month=month, year=year, target=target))[0][0]
    except:
        return 0
    return qty
    
def last_day_of_month(year, month):
    return (datetime.date(year, (month % 12) + 1, 1) - datetime.timedelta(days=1)).day
    
def get_turnover(year, month, accounts, company):
    amount = frappe.db.sql("""SELECT IFNULL((SUM(`tabGL Entry`.`credit`) - SUM(`tabGL Entry`.`debit`)), 0)
            FROM `tabGL Entry` 
            LEFT JOIN `tabAccount` ON `tabAccount`.`name` = `tabGL Entry`.`account`
            WHERE 
                `tabAccount`.`account_number` IN ({accounts})
                AND `tabGL Entry`.`posting_date` LIKE "{year}-{month:02d}%"
                AND `tabGL Entry`.`company` = "{company}";
            """.format(month=month, year=year, accounts=", ".join(accounts), company=company))[0][0]
    return amount
    
def get_turnover_ytd(year, month, accounts, company):
    amount = frappe.db.sql("""SELECT IFNULL((SUM(`tabGL Entry`.`credit`) - SUM(`tabGL Entry`.`debit`)), 0)
            FROM `tabGL Entry` 
            LEFT JOIN `tabAccount` ON `tabAccount`.`name` = `tabGL Entry`.`account`
            WHERE 
                `tabAccount`.`account_number` IN ({accounts})
                AND `tabGL Entry` .`posting_date` >= "{year}-01-01"
                AND `tabGL Entry` .`posting_date` <= "{year}-{month:02d}-{last_day}"
                AND `tabGL Entry`.`company` = "{company}";
            """.format(month=month, year=year, accounts=", ".join(accounts), 
                last_day=last_day_of_month(year, month), company=company))[0][0]
    return amount
    
def get_turnover_budget(year, month, accounts, company):
    try:
        amount = frappe.db.sql("""SELECT 
                IFNULL((`tabMonthly Distribution Percentage`.`percentage_allocation` * `tabBudget Account`.`budget_amount` / 100), 0)
            FROM `tabBudget` 
            LEFT JOIN `tabMonthly Distribution Percentage` ON `tabMonthly Distribution Percentage`.`parent` = `tabBudget`.`monthly_distribution`
            LEFT JOIN `tabBudget Account` ON `tabBudget Account`.`parent` = `tabBudget`.`name`
            LEFT JOIN `tabAccount` ON `tabAccount`.`name` = `tabBudget Account`.`account`
            WHERE 
              `tabBudget`.`fiscal_year` = "{year}"
              AND `tabBudget`.`docstatus` < 2
              AND `tabBudget`.`company` = "{company}"
              AND `tabMonthly Distribution Percentage`.`idx` = {month}
              AND `tabAccount`.`account_number` IN ({accounts})
              ;
                """.format(month=month, year=year, accounts=", ".join(accounts), company=company))[0][0]
    except:
        return 0
    return amount
    
def get_turnover_budget_ytd(year, month, accounts, company):
    try:
        amount = frappe.db.sql("""SELECT 
                IFNULL(SUM(`tabMonthly Distribution Percentage`.`percentage_allocation` * `tabBudget Account`.`budget_amount` / 100), 0)
            FROM `tabBudget` 
            LEFT JOIN `tabMonthly Distribution Percentage` ON `tabMonthly Distribution Percentage`.`parent` = `tabBudget`.`monthly_distribution`
            LEFT JOIN `tabBudget Account` ON `tabBudget Account`.`parent` = `tabBudget`.`name`
            LEFT JOIN `tabAccount` ON `tabAccount`.`name` = `tabBudget Account`.`account`
            WHERE 
              `tabBudget`.`fiscal_year` = "{year}"
              AND `tabBudget`.`docstatus` < 2
              AND `tabBudget`.`company` = "{company}"
              AND `tabMonthly Distribution Percentage`.`idx` <= {month}
              AND `tabAccount`.`account_number` IN ({accounts});
                """.format(month=month, year=year, accounts=", ".join(accounts), 
                    last_day=last_day_of_month(year, month), company=company))[0][0]
    except:
        return 0
    return amount
