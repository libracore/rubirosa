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
        'month_last_year': get_currency_str(get_turnover(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_month_this_year': get_currency_str(get_turnover_budget(filters.year, filters.month, accounts, filters.company)),
        'month_this_year': get_currency_str(get_turnover(filters.year, filters.month, accounts, filters.company)),
        'last_year': get_currency_str(get_turnover_ytd(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_this_year': get_currency_str(get_turnover_budget_ytd(filters.year, filters.month, accounts, filters.company)),
        'this_year': get_currency_str(get_turnover_ytd(filters.year, filters.month, accounts, filters.company))
    })
    
    accounts = ["3410"]
    data.append({
        'description': '-Commission Agents (CHF) (3410)',
        'month_last_year': get_currency_str(get_turnover(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_month_this_year': get_currency_str((-1) * get_turnover_budget(filters.year, filters.month, accounts, filters.company)),
        'month_this_year': get_currency_str(get_turnover(filters.year, filters.month, accounts, filters.company)),
        'last_year': get_currency_str(get_turnover_ytd(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_this_year': get_currency_str((-1) * get_turnover_budget_ytd(filters.year, filters.month, accounts, filters.company)),
        'this_year': get_currency_str(get_turnover_ytd(filters.year, filters.month, accounts, filters.company))
    })
    
    accounts = ["3408", "3480", "3490"]
    data.append({
        'description': '-Factoring / Skonto (CHF) (3408, 3480, 3490)',
        'month_last_year': get_currency_str(get_turnover(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_month_this_year': get_currency_str((-1) * get_turnover_budget(filters.year, filters.month, accounts, filters.company)),
        'month_this_year': get_currency_str(get_turnover(filters.year, filters.month, accounts, filters.company)),
        'last_year': get_currency_str(get_turnover_ytd(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_this_year': get_currency_str((-1) * get_turnover_budget_ytd(filters.year, filters.month, accounts, filters.company)),
        'this_year': get_currency_str(get_turnover_ytd(filters.year, filters.month, accounts, filters.company))
    })
    
    # growing rate revenue
    net_revenue_month = get_float(data[-3]['month_this_year']) + get_float(data[-2]['month_this_year']) + get_float(data[-1]['month_this_year'])
    net_revenue_month_py = get_float(data[-3]['month_last_year']) + get_float(data[-2]['month_last_year']) + get_float(data[-1]['month_last_year'])
    net_revenue_year = (get_float(data[-3]['this_year']) + get_float(data[-2]['this_year']) + get_float(data[-1]['this_year']))
    net_revenue_py = get_float(data[-3]['last_year']) + get_float(data[-2]['last_year']) + get_float(data[-1]['last_year'])

    #avg_revenue_year = net_revenue_year / filters.month
    budget_month = get_float(data[-3]['budget_month_this_year']) + get_float(data[-2]['budget_month_this_year']) + get_float(data[-1]['budget_month_this_year'])
    budget_year = (get_float(data[-3]['budget_this_year']) + get_float(data[-2]['budget_this_year']) + get_float(data[-1]['budget_this_year']))
    #avg_budget_year = budget_year / filters.month
    data.append({
        'description': 'Growing Rate Gross Revenue',
        'month_last_year': "",
        'budget_month_this_year': "",
        'month_this_year': "{:,.2f}%".format(100 * (net_revenue_month - net_revenue_month_py) / net_revenue_month_py).replace(",", "'"),
        'last_year': "",
        'budget_this_year': "",
        'this_year': "{:,.2f}%".format(100 * (net_revenue_year - net_revenue_py) / net_revenue_py).replace(",", "'")
    })
    data.append({
        'description': 'Operational Revenue (CHF)',
        'month_last_year': get_currency_str(net_revenue_month_py),
        'budget_month_this_year': get_currency_str(budget_month),
        'month_this_year': get_currency_str(net_revenue_month),
        'last_year': get_currency_str(net_revenue_py),
        'budget_this_year': get_currency_str(budget_year),
        'this_year': get_currency_str(net_revenue_year)
    })
    
    # COGS
    accounts = ["4400"]
    data.append({
        'description': '-Cost of Goods Produced (CHF) (4400)',
        'month_last_year': get_currency_str(get_turnover(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_month_this_year': get_currency_str((-1) * get_turnover_budget(filters.year, filters.month, accounts, filters.company)),
        'month_this_year': get_currency_str(get_turnover(filters.year, filters.month, accounts, filters.company)),
        'last_year': get_currency_str(get_turnover_ytd(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_this_year': get_currency_str((-1) * get_turnover_budget_ytd(filters.year, filters.month, accounts, filters.company)),
        'this_year': get_currency_str(get_turnover_ytd(filters.year, filters.month, accounts, filters.company))
    })
    
    accounts = ["4401", "4402", "4403", "4404", "4405", "4406", "4407", "4409", "4470"]
    data.append({
        'description': '-Related Costs (Samples, Transport, etc.) (CHF) (4401-4470)',
        'month_last_year': get_currency_str(get_turnover(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_month_this_year': get_currency_str((-1) * get_turnover_budget(filters.year, filters.month, accounts, filters.company)),
        'month_this_year': get_currency_str(get_turnover(filters.year, filters.month, accounts, filters.company)),
        'last_year': get_currency_str(get_turnover_ytd(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_this_year': get_currency_str((-1) * get_turnover_budget_ytd(filters.year, filters.month, accounts, filters.company)),
        'this_year': get_currency_str(get_turnover_ytd(filters.year, filters.month, accounts, filters.company))
    })
    
    # gross profit
    gross_profit_month = get_float(data[-3]['month_this_year']) + get_float(data[-2]['month_this_year']) + get_float(data[-1]['month_this_year'])
    gross_profit_month_py = get_float(data[-3]['month_last_year']) + get_float(data[-2]['month_last_year']) + get_float(data[-1]['month_last_year'])
    gross_profit_year = (get_float(data[-3]['this_year']) + get_float(data[-2]['this_year']) + get_float(data[-1]['this_year']))
    gross_profit_py = get_float(data[-3]['last_year']) + get_float(data[-2]['last_year']) + get_float(data[-1]['last_year'])
    budget_gross_profit_month = get_float(data[-3]['budget_month_this_year']) + get_float(data[-2]['budget_month_this_year']) + get_float(data[-1]['budget_month_this_year'])
    budget_gross_profit_year = (get_float(data[-3]['budget_this_year']) + get_float(data[-2]['budget_this_year']) + get_float(data[-1]['budget_this_year']))
    data.append({
        'description': 'Gross Profit (CHF)',
        'month_last_year': get_currency_str(gross_profit_month_py),
        'budget_month_this_year': get_currency_str(budget_gross_profit_month),
        'month_this_year': get_currency_str(gross_profit_month),
        'last_year': get_currency_str(gross_profit_py),
        'budget_this_year': get_currency_str(budget_gross_profit_year),
        'this_year': get_currency_str(gross_profit_year)
    })
    data.append({
        'description': 'Gross Profit in %',
        'month_last_year': get_percent_str((100 * (gross_profit_month_py) / net_revenue_month_py) if net_revenue_month_py else 0),
        'budget_month_this_year': get_percent_str((100 * (budget_gross_profit_month) / budget_month) if budget_month else 0),
        'month_this_year': get_percent_str((100 * (gross_profit_month) / net_revenue_month) if net_revenue_month else 0),
        'last_year': get_percent_str((100 * (gross_profit_py) / net_revenue_py) if net_revenue_py else 0),
        'budget_this_year': get_percent_str((100 * (budget_gross_profit_year) / budget_year) if budget_year else 0),
        'this_year': get_percent_str((100 * (gross_profit_year) / net_revenue_month) if net_revenue_month else 0)
    })
    data.append({
        'description': 'Growing Rate Gross Profit',
        'month_last_year': "",
        'budget_month_this_year': "",
        'month_this_year': get_percent_str(100 * (gross_profit_month - gross_profit_month_py) / gross_profit_month_py),
        'last_year': "",
        'budget_this_year': "",
        'this_year': get_percent_str(100 * (gross_profit_year - gross_profit_py) / gross_profit_py)
    })
    data.append({
        'description': ''
    })
    
    # other expenses
    accounts = ["5000", "5001", "5700", "5720", "5730", "5740", "5810", "5880", "5900"]
    data.append({
        'description': 'Salaries (FTE) (CHF) (5000-5900)',
        'month_last_year': get_currency_str(get_turnover(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_month_this_year': get_currency_str((-1) * get_turnover_budget(filters.year, filters.month, accounts, filters.company)),
        'month_this_year': get_currency_str(get_turnover(filters.year, filters.month, accounts, filters.company)),
        'last_year': get_currency_str(get_turnover_ytd(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_this_year': get_currency_str((-1) * get_turnover_budget_ytd(filters.year, filters.month, accounts, filters.company)),
        'this_year': get_currency_str(get_turnover_ytd(filters.year, filters.month, accounts, filters.company))
    })
    accounts = ["6600", "6601", "6602", "6610", "6620", "6621", "6640"]
    data.append({
        'description': 'Marketing (CHF) (6600-6640)',
        'month_last_year': get_currency_str(get_turnover(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_month_this_year': get_currency_str((-1) * get_turnover_budget(filters.year, filters.month, accounts, filters.company)),
        'month_this_year': get_currency_str(get_turnover(filters.year, filters.month, accounts, filters.company)),
        'last_year': get_currency_str(get_turnover_ytd(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_this_year': get_currency_str((-1) * get_turnover_budget_ytd(filters.year, filters.month, accounts, filters.company)),
        'this_year': get_currency_str(get_turnover_ytd(filters.year, filters.month, accounts, filters.company))
    })
    accounts = ["6000", "6001", "6200", "6300", "6500", "6501", "6510", "6513", "6520", "6530", "6531", "6532", "6540", "6570", "6576"]
    data.append({
        'description': 'Other expenses (CHF) (6000, 6001, 6200, 6300, 6500-6576)',
        'month_last_year': get_currency_str(get_turnover(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_month_this_year': get_currency_str((-1) * get_turnover_budget(filters.year, filters.month, accounts, filters.company)),
        'month_this_year': get_currency_str(get_turnover(filters.year, filters.month, accounts, filters.company)),
        'last_year': get_currency_str(get_turnover_ytd(filters.year - 1, filters.month, accounts, filters.company)),
        'budget_this_year': get_currency_str((-1) * get_turnover_budget_ytd(filters.year, filters.month, accounts, filters.company)),
        'this_year': get_currency_str(get_turnover_ytd(filters.year, filters.month, accounts, filters.company))
    })
    expenses_month = get_float(data[-3]['month_this_year']) + get_float(data[-2]['month_this_year']) + get_float(data[-1]['month_this_year'])
    expenses_month_py = get_float(data[-3]['month_last_year']) + get_float(data[-2]['month_last_year']) + get_float(data[-1]['month_last_year'])
    expenses_year = (get_float(data[-3]['this_year']) + get_float(data[-2]['this_year']) + get_float(data[-1]['this_year']))
    expenses_py = get_float(data[-3]['last_year']) + get_float(data[-2]['last_year']) + get_float(data[-1]['last_year'])
    budget_expenses_month = get_float(data[-3]['budget_month_this_year']) + get_float(data[-2]['budget_month_this_year']) + get_float(data[-1]['budget_month_this_year'])
    budget_expenses_year = (get_float(data[-3]['budget_this_year']) + get_float(data[-2]['budget_this_year']) + get_float(data[-1]['budget_this_year']))
    data.append({
        'description': 'Total (CHF)',
        'month_last_year': get_currency_str(expenses_month_py),
        'budget_month_this_year': get_currency_str(budget_expenses_month),
        'month_this_year': get_currency_str(expenses_month),
        'last_year': get_currency_str(expenses_py),
        'budget_this_year': get_currency_str(budget_expenses_year),
        'this_year': get_currency_str(expenses_year)
    })
    data.append({
        'description': 'Growing Rate \"Other Expenses\"',
        'month_last_year': "",
        'budget_month_this_year': "",
        'month_this_year': get_percent_str((100 * (expenses_month - expenses_month_py) / expenses_month_py) if expenses_month_py else 0),
        'last_year': "",
        'budget_this_year': "",
        'this_year': get_percent_str((100 * (expenses_year - expenses_py) / expenses_py) if expenses_py else 0)
    })
    data.append({
        'description': ''
    })
    
    # EBITDA
    ebitda_month = gross_profit_month + expenses_month
    ebitda_month_py = gross_profit_month_py + expenses_month_py
    ebitda_year = gross_profit_year + expenses_year
    ebitda_py = gross_profit_py + expenses_py
    budget_ebitda_month = budget_gross_profit_month + budget_expenses_month
    budget_ebitda_year = budget_gross_profit_year + budget_expenses_year
    data.append({
        'description': 'Total (CHF)',
        'month_last_year': get_currency_str(ebitda_month_py),
        'budget_month_this_year': get_currency_str(budget_ebitda_month),
        'month_this_year': get_currency_str(ebitda_month),
        'last_year': get_currency_str(ebitda_py),
        'budget_this_year': get_currency_str(budget_ebitda_year),
        'this_year': get_currency_str(ebitda_year)
    })
    data.append({
        'description': 'Growing Rate EBITDA',
        'month_last_year': "",
        'budget_month_this_year': "",
        'month_this_year': get_percent_str((100 * (ebitda_month - ebitda_month_py) / ebitda_month_py) if ebitda_month_py else 0),
        'last_year': "",
        'budget_this_year': "",
        'this_year': get_percent_str((100 * (ebitda_year - ebitda_py) / ebitda_py) if ebitda_py else 0)
    })
    data.append({
        'description': ''
    })
    
    # sales per customer group
    data.append({
        'description': '<b>Sales per Customer Group / Total</b>',
        'month_last_year': "<b>{0}-{1} (CHF)</b>".format(filters.year - 1, filters.month),
        'budget_month_this_year': "<b>{0}-{1} (pcs)</b>".format(filters.year, filters.month),
        'month_this_year': "<b>{0}-{1} (CHF)</b>".format(filters.year, filters.month),
        'last_year': "<b>{0} (CHF)</b>".format(filters.year - 1),
        'budget_this_year': "<b>{0} (pcs)</b>".format(filters.year),
        'this_year': "<b>{0} (CHF)</b>".format(filters.year)
    })
    data.append({
        'description': 'Retail Customer',
        'month_last_year': get_currency_str(get_amount(filters.year - 1, filters.month, filters.company, customer_group="Retail Customer")),
        'budget_month_this_year': get_qty_str(get_qty(filters.year, filters.month, filters.company, customer_group="Retail Customer")),
        'month_this_year': get_currency_str(get_amount(filters.year, filters.month, filters.company, customer_group="Retail Customer")),
        'last_year': get_currency_str(get_amount_ytd(filters.year - 1, filters.month, filters.company, customer_group="Retail Customer")),
        'budget_this_year': get_qty_str(get_qty_ytd(filters.year, filters.month, filters.company, customer_group="Retail Customer")),
        'this_year': get_currency_str(get_amount_ytd(filters.year, filters.month, filters.company, customer_group="Retail Customer"))
    })
    data.append({
        'description': 'Online Customer',
        'month_last_year': get_currency_str(get_amount(filters.year - 1, filters.month, filters.company, customer_group="Online Customer")),
        'budget_month_this_year': get_qty_str(get_qty(filters.year, filters.month, filters.company, customer_group="Online Customer")),
        'month_this_year': get_currency_str(get_amount(filters.year, filters.month, filters.company, customer_group="Online Customer")),
        'last_year': get_currency_str(get_amount_ytd(filters.year - 1, filters.month, filters.company, customer_group="Online Customer")),
        'budget_this_year': get_qty_str(get_qty_ytd(filters.year, filters.month, filters.company, customer_group="Online Customer")),
        'this_year': get_currency_str(get_amount_ytd(filters.year, filters.month, filters.company, customer_group="Online Customer"))
    })
    data.append({
        'description': 'Outlet',
        'month_last_year': get_currency_str(get_amount(filters.year - 1, filters.month, filters.company, customer_group="Outlet")),
        'budget_month_this_year': get_qty_str(get_qty(filters.year, filters.month, filters.company, customer_group="Outlet")),
        'month_this_year': get_currency_str(get_amount(filters.year, filters.month, filters.company, customer_group="Outlet")),
        'last_year': get_currency_str(get_amount_ytd(filters.year - 1, filters.month, filters.company, customer_group="Outlet")),
        'budget_this_year': get_qty_str(get_qty_ytd(filters.year, filters.month, filters.company, customer_group="Outlet")),
        'this_year': get_currency_str(get_amount_ytd(filters.year, filters.month, filters.company, customer_group="Outlet"))
    })
    data.append({
        'description': 'RR Friends',
        'month_last_year': get_currency_str(get_amount(filters.year - 1, filters.month, filters.company, customer_group="RR Friends")),
        'budget_month_this_year': get_qty_str(get_qty(filters.year, filters.month, filters.company, customer_group="RR Friends")),
        'month_this_year': get_currency_str(get_amount(filters.year, filters.month, filters.company, customer_group="RR Friends")),
        'last_year': get_currency_str(get_amount_ytd(filters.year - 1, filters.month, filters.company, customer_group="RR Friends")),
        'budget_this_year': get_qty_str(get_qty_ytd(filters.year, filters.month, filters.company, customer_group="RR Friends")),
        'this_year': get_currency_str(get_amount_ytd(filters.year, filters.month, filters.company, customer_group="RR Friends"))
    })
    full_amount_month = get_amount(filters.year, filters.month, filters.company)
    full_amount_month_py = get_amount(filters.year - 1, filters.month, filters.company)
    full_amount_year = get_amount_ytd(filters.year, filters.month, filters.company)
    full_amount_py = get_amount_ytd(filters.year - 1, filters.month, filters.company)
    full_qty_month = get_qty(filters.year, filters.month, filters.company)
    full_qty_year = get_qty_ytd(filters.year, filters.month, filters.company)
    
    recorded_amount_month = 0
    recorded_amount_month_py = 0
    recorded_amount_year = 0
    recorded_amount_py = 0
    recorded_qty_month = 0
    recorded_qty_year = 0
    for i in range(-4, 0, +1):
        recorded_amount_month += get_float(data[i]['month_this_year'])
        recorded_amount_month_py += get_float(data[i]['month_last_year'])
        recorded_amount_year += get_float(data[i]['this_year'])
        recorded_amount_py += get_float(data[i]['last_year'])
        recorded_qty_month += get_float(data[i]['budget_month_this_year'])
        recorded_qty_year += get_float(data[i]['budget_this_year'])
    
    data.append({
        'description': 'Others (Stylist, Showroom, etc.)',
        'month_last_year': get_currency_str(full_amount_month_py - recorded_amount_month_py),
        'budget_month_this_year': get_qty_str(full_qty_month - recorded_qty_month),
        'month_this_year': get_currency_str(full_amount_month - recorded_amount_month),
        'last_year': get_currency_str(full_amount_py - recorded_amount_py),
        'budget_this_year': get_qty_str(full_qty_year - recorded_qty_year),
        'this_year': get_currency_str(full_amount_year - recorded_amount_year)
    })
    
    return data

def get_float(s):
    return float(s.split(" ")[0].replace("'", ""))

def get_currency_str(v):
    return "{:,.2f}".format(v).replace(",", "'")
    
def get_percent_str(v):
    return "{:,.2f}%".format(v).replace(",", "'")

def get_qty_str(v):
    return "{:,.0f} pcs".format(v).replace(",", "'")
    
def get_qty(year, month, company, online=False, customer_group=None):
    if customer_group:
        condition = """ AND `tabSales Invoice`.`customer_group` = "{0}" """.format(customer_group)
    else:
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
    
def get_qty_ytd(year, month, company, online=False, customer_group=None):
    if customer_group:
        condition = """ AND `tabSales Invoice`.`customer_group` = "{0}" """.format(customer_group)
    else:
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

def get_amount(year, month, company, customer_group=None):
    condition = """ AND `tabSales Invoice`.`customer_group` LIKE "{0}" """.format(customer_group) if customer_group else ""
    
    qty = frappe.db.sql("""SELECT IFNULL(SUM(`base_amount`), 0)
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
    
def get_amount_ytd(year, month, company, customer_group=None):
    condition = """ AND `tabSales Invoice`.`customer_group` LIKE "{0}" """.format(customer_group) if customer_group else ""
    
    qty = frappe.db.sql("""SELECT IFNULL(SUM(`base_amount`), 0)
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
    target = "qtys_online" if online else "qtys"
    
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
