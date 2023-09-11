# Copyright (c) 2013, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns(filters)
    data = get_data(filters)
    
    return columns, data

def get_columns(filters):
    if filters.sinv_type == "Invoices":
        return [
            {"label": _("Anrede"), "fieldname": "salutation", "fieldtype": "Data", "width": 100},
            {"label": _("Vorname"), "fieldname": "first_name", "fieldtype": "Data", "width": 100},
            {"label": _("Kundenname"), "fieldname": "customer_name", "fieldtype": "Data", "width": 100},
            {"label": _("Adresszusatz"), "fieldname": "address_addition", "fieldtype": "Data", "width": 100},
            {"label": _("Branche"), "fieldname": "branch", "fieldtype": "Data", "width": 100},
            {"label": _("Strasse"), "fieldname": "street", "fieldtype": "Data", "width": 100},
            {"label": _("Postfach"), "fieldname": "mailbox", "fieldtype": "Data", "width": 100},
            {"label": _("Land"), "fieldname": "country", "fieldtype": "Data", "width": 100},
            {"label": _("PLZ"), "fieldname": "pincode", "fieldtype": "Data", "width": 100},
            {"label": _("Ort"), "fieldname": "city", "fieldtype": "Data", "width": 100},
            {"label": _("Sprache"), "fieldname": "language", "fieldtype": "Data", "width": 100},
            {"label": _("Re.datum"), "fieldname": "sinv_date", "fieldtype": "Data", "width": 100},
            {"label": _("Re.nummer"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 100},
            {"label": _("ESR-Referenz"), "fieldname": "esr_reference", "fieldtype": "Data", "width": 100},
            {"label": _("Re.betrag"), "fieldname": "amount", "fieldtype": "Currency", "width": 100},
            {"label": _("Zahlungsziel"), "fieldname": "payment_target", "fieldtype": "Date", "width": 100},
            {"label": _("Skonto/Rabatt"), "fieldname": "discounts", "fieldtype": "Float", "precision": 2, "width": 100},
            {"label": _("Skontofrist"), "fieldname": "discount_period", "fieldtype": "Int", "width": 100}
        ]
    elif filters.sinv_type == "Returns":
        return [
            {"label": _("Kundenname"), "fieldname": "customer_name", "fieldtype": "Data", "width": 100},
            {"label": _("Adresszusatz"), "fieldname": "address_addition", "fieldtype": "Data", "width": 100},
            {"label": _("Branche"), "fieldname": "branch", "fieldtype": "Data", "width": 100},
            {"label": _("Strasse"), "fieldname": "street", "fieldtype": "Data", "width": 100},
            {"label": _("Postfach"), "fieldname": "mailbox", "fieldtype": "Data", "width": 100},
            {"label": _("Land"), "fieldname": "country", "fieldtype": "Data", "width": 100},
            {"label": _("PLZ"), "fieldname": "pincode", "fieldtype": "Data", "width": 100},
            {"label": _("Ort"), "fieldname": "city", "fieldtype": "Data", "width": 100},
            {"label": _("Sprache"), "fieldname": "language", "fieldtype": "Data", "width": 100},
            {"label": _("GS-Datum"), "fieldname": "sinv_date", "fieldtype": "Data", "width": 100},
            {"label": _("GS-Nr."), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 100},
            {"label": _("GS-Betrag"), "fieldname": "amount", "fieldtype": "Currency", "width": 100}
        ]
    
def get_data(filters):
    sinv_filter = ''
    amount = ''
    no_pre_payments = ''
    if filters.sinv_type == "Invoices":
        sinv_filter = """WHERE `sinv`.`is_return` = 0"""
        amount = """`sinv`.`grand_total` AS `amount`"""
        no_pre_payments = """AND `sinv`.`name` NOT IN (
                                SELECT `parent` FROM `tabSales Invoice Item`
                                WHERE `sales_order` IN (
                                    SELECT `name` FROM `tabSales Order`
                                    WHERE `woocommerce_payment_method` = 'Payrexx (Credit Card, Apple Pay, Google Pay, GiroPay, Sofort)'
                                )
                            )"""
    elif filters.sinv_type == "Returns":
        sinv_filter = """WHERE `sinv`.`is_return` = 1"""
        amount = """(`sinv`.`grand_total` * -1) AS `amount`"""
    
    date = ""
    if filters.from_date:
            date = """AND `sinv`.`posting_date` BETWEEN '{0}' AND '{1}'""".format(filters.from_date, filters.end_date)
    
    data = frappe.db.sql("""
                            SELECT
                                `sinv`.`customer_name`,
                                `sinv`.`posting_date` AS `sinv_date`,
                                `sinv`.`name` AS `sales_invoice`,
                                `sinv`.`esr_reference`,
                                {amount},
                                `sinv`.`due_date` AS `payment_target`,
                                `sinv`.`discount_amount` AS `discounts`,
                                `addr`.`address_line1` AS `street`,
                                `addr`.`address_line2` AS `address_addition`,
                                `addr`.`country`,
                                `addr`.`pincode`,
                                `addr`.`city`,
                                `cont`.`first_name`,
                                `cont`.`salutation`,
                                `cust`.`customer_group` AS `branch`,
                                `cust`.`language`
                            FROM `tabSales Invoice` AS `sinv`
                            LEFT JOIN `tabAddress` AS `addr` ON `sinv`.`customer_address` = `addr`.`name`
                            LEFT JOIN `tabContact` AS `cont` ON `sinv`.`contact_person` = `cont`.`name`
                            LEFT JOIN `tabCustomer` AS `cust` ON `sinv`.`customer` = `cust`.`name`
                            {sinv_filter}
                            {no_pre_payments}
                            {date}
                        """.format(amount=amount, sinv_filter=sinv_filter, no_pre_payments=no_pre_payments, date=date), as_dict=True)

    return data
