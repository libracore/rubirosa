# Copyright (c) 2013-2021, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    
    columns = [
        {'fieldname': 'sales_partner', 'label': _('Sales Partner'), 'fieldtype': 'Link', 'options': 'Sales Partner', 'width': 150}, 
        {'fieldname': 'order_date', 'label': _('Order Date'), 'fieldtype': 'Date', 'width': 100}, 
        {'fieldname': 'sales_order', 'label': _('Sales Order'), 'fieldtype': 'Link', 'options': 'Sales Order', 'width': 100}, 
        {'fieldname': 'sales_season', 'label': _('Sales Season'), 'fieldtype': 'Link', 'options': 'Monthly Distribution', 'width': 150}, 
        {'fieldname': 'date', 'label': _('Date'), 'fieldtype': 'Date', 'width': 80}, 
        {'fieldname': 'sales_invoice', 'label': _('Sales Invoice'), 'fieldtype': 'Link', 'options': 'Sales Invoice', 'width': 150}, 
        {'fieldname': 'customer_name', 'label': _('Customer'), 'fieldtype': 'Data', 'width': 150}, 
        {'fieldname': 'base_amount', 'label': _('Invoiced Amount (Exclusive Tax)'), 'fieldtype': 'Currency', 'width': 210}, 
        {'fieldname': 'amount', 'label': _('Amount'), 'fieldtype': 'Float', 'precision': 2, 'width': 80}, 
        {'fieldname': 'currency', 'label': _('Currency'), 'fieldtype': 'Data', 'width': 50}, 
        {'fieldname': 'total_commission', 'label': 'Total Commission', 'fieldtype': 'Currency', 'width': 150}, 
        {'fieldname': 'avg_commission', 'label': 'Average Commission Rate', 'fieldtype': 'Percent', 'width': 170}
    ]
    
    if not filters.from_date:
        filters.from_date = "2000-01-01"
    if not filters.end_date:
        filters.end_date = "2999-12-31"

    if filters.sales_partner:
        conditions = """ AND `tabSales Invoice`.`sales_partner` = "{0}" """.format(filters.sales_partner)
    else:
        conditions = ""
        
    data = frappe.db.sql("""SELECT
            `tabSales Invoice`.`sales_partner` AS `sales_partner`,
            `tabSales Invoice`.`name` AS `sales_invoice`,
            DATE(`tabSales Order`.`transaction_date`) AS `order_date`,
            `tabSales Order`.`name` AS `sales_order`,
            `tabSales Order`.`sales_season` AS `sales_season`,
            `tabSales Invoice`.`posting_date` AS `date`,
            `tabSales Invoice`.`base_net_total` AS `base_amount`,
            `tabSales Invoice`.`net_total` AS `amount`,
            `tabSales Invoice`.`total_commission` AS `total_commission`,
            100 * `tabSales Invoice`.`total_commission` / `tabSales Invoice`.`base_net_total` AS `avg_commission`,
            `tabSales Invoice`.`customer_name` AS `customer_name`,
            `tabSales Invoice`.`currency` AS `currency`
        FROM `tabSales Invoice`
        LEFT JOIN `tabSales Partner` ON `tabSales Partner`.`name` = `tabSales Invoice`.`sales_partner`
        LEFT JOIN `tabSales Invoice Item` ON `tabSales Invoice Item`.`parent` = `tabSales Invoice`.`name` 
                                             AND `tabSales Invoice Item`.`idx` = 1
        LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabSales Invoice Item`.`sales_Order`
        WHERE
            `tabSales Invoice`.`docstatus` = 1 
            AND `tabSales Invoice`.`posting_date` >= "{start_date}"
            AND `tabSales Invoice`.`posting_date` <= "{end_date}"
            AND IFNULL(`tabSales Invoice`.`base_net_total`, 0) != 0 
            AND IFNULL(`tabSales Invoice`.`total_commission`, 0) != 0
            {conditions}
        ORDER BY `tabSales Invoice`.`sales_partner` ASC, `tabSales Invoice`.`name` DESC
            ;""".format(
            start_date=filters.from_date, end_date=filters.end_date, conditions=conditions), as_dict = True)

    return columns, data
