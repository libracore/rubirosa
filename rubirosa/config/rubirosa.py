from __future__ import unicode_literals
from frappe import _

def get_data():
    return[
        {
            "label": _("Marketing"),
            "icon": "fa fa-money",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Customer",
                       "label": _("Customer"),
                       "description": _("Customer")
                   },
                   {
                       "type": "doctype",
                       "name": "Campaign",
                       "label": _("Campaign"),
                       "description": _("Campaign")
                   },
                   {
                       "type": "doctype",
                       "name": "Marketing Material",
                       "label": _("Marketing Material"),
                       "description": _("Marketing Material")
                   },
                   {
                       "type": "page",
                       "name": "customer-overview",
                       "label": _("Customer Overview"),
                        "description": _("Customer Overview")
                   }
            ]
        },
        {
            "label": _("Manufacturing"),
            "icon": "fa fa-bank",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Specification",
                       "label": _("Specification"),
                       "description": _("Specification")
                   },
                   {
                       "type": "report",
                       "doctype": "Sales Order",
                       "name": "Order Planning",
                       "label": _("Order Planning"),
                       "description": _("Order Planning"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Sales Order",
                       "name": "Order Planning for Reorder",
                       "label": _("Order Planning for Reorder"),
                       "description": _("Order Planning for Reorder"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Purchase Receipt",
                       "name": "Purchase Receipt Mapping",
                       "label": _("Purchase Receipt Mapping"),
                       "description": _("Purchase Receipt Mapping"),
                       "is_query_report": True
                   },
                   {
                       "type": "doctype",
                       "name": "Etikettenbogen",
                       "label": _("Etikettenbogen"),
                       "description": _("Etikettenbogen")
                   }
            ]
        },
        {
            "label": _("Integrations"),
            "icon": "fa fa-bank",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Shipment",
                       "label": _("Shipment"),
                       "description": _("Shipment")
                   },
                   {
                       "type": "doctype",
                       "name": "WooCommerce Settings",
                       "label": _("WooCommerce Settings"),
                       "description": _("WooCommerce Settings")
                   },
                   {
                       "type": "page",
                       "name": "sync_mailchimp",
                       "label": _("Sync MailChimp"),
                       "description": _("Sync MailChimp")                   
                   },
                   {
                       "type": "doctype",
                       "name": "Multisped Settings",
                       "label": _("Multisped Settings"),
                       "description": _("Multisped Settings")
                   },
                   {
                       "type": "doctype",
                       "name": "Multisped Log",
                       "label": _("Multisped Log"),
                       "description": _("Multisped Log")
                   },
                   {
                       "type": "doctype",
                       "name": "Multisped Transfer Record",
                       "label": _("Multisped Transfer Record"),
                       "description": _("Multisped Transfer Record")
                   }
            ]
        },
        {
            "label": _("Sales"),
            "icon": "octicon octicon-file-submodule",
            "items": [
                   {
                       "type": "doctype",
                       "name": "Sales Invoice",
                       "label": _("Sales Invoice"),
                       "description": _("Sales Invoice")                   
                   },
                   {
                       "type": "doctype",
                       "name": "Pricelist Print",
                       "label": _("Pricelist Print"),
                       "description": _("Pricelist Print")                   
                   },
                   {
                       "type": "report",
                       "doctype": "Sales Invoice",
                       "name": "Advanced Sales Partners Commission",
                       "label": _("Advanced Sales Partners Commission"),
                       "description": _("Advanced Sales Partners Commission"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Sales Invoice",
                       "name": "Advanced Sales Partners Commission Detail rubirosa",
                       "label": _("Advanced Sales Partners Commission Detail"),
                       "description": _("Advanced Sales Partners Commission Detail"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Sales Invoice",
                       "name": "Customer Statistics",
                       "label": _("Customer Statistics"),
                       "description": _("Customer Statistics"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Sales Invoice",
                       "name": "Order Overview",
                       "label": _("Order Overview"),
                       "description": _("Order Overview"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Sales Invoice",
                       "name": "Debitoren Export",
                       "label": _("Debitoren Export"),
                       "description": _("Debitoren Export"),
                       "is_query_report": True
                   }
            ]
        },
        {
            "label": _("Accounting"),
            "icon": "fa fa-bank",
            "items": [
                   {
                       "type": "report",
                       "doctype": "GL Entry",
                       "name": "General Ledger",
                       "label": _("General Ledger"),
                       "description": _("General Ledger"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "GL Entry",
                       "name": "Liquidity Plan",
                       "label": _("Liquidity Plan"),
                       "description": _("Liquidity Plan"),
                       "is_query_report": True
                   },
                   {
                       "type": "doctype",
                       "name": "Budget",
                       "label": _("Budget"),
                       "description": _("Budget")                   
                   },
                   {
                       "type": "doctype",
                       "name": "Budget Qty",
                       "label": _("Budget Qty"),
                       "description": _("Budget Qty")                   
                   }
            ]
        },
        {
            "label": _("Business Intelligence"),
            "icon": "fa fa-tools",
            "items": [
                   {
                       "type": "report",
                       "doctype": "Sales Invoice",
                       "name": "Verkaufsanalyse Pivot",
                       "label": _("Verkaufsanalyse Pivot"),
                       "description": _("Verkaufsanalyse Pivot"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Customer",
                       "name": "Customer Statistics",
                       "label": _("Customer Statistics"),
                       "description": _("Customer Statistics"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Account",
                       "name": "Liquidity Plan",
                       "label": _("Liquidity Plan"),
                       "description": _("Liquidity Plan"),
                       "is_query_report": True
                   },
                   {
                       "type": "report",
                       "doctype": "Budget",
                       "name": "Monthly Investors Report",
                       "label": _("Monthly Investors Report"),
                       "description": _("Monthly Investors Report"),
                       "is_query_report": True
                   }
            ]
        },
        {
            "label": _("EDI"),
            "icon": "octicon octicon-git-compare",
            "items": [
                   {
                       "type": "doctype",
                       "name": "EDI Connection",
                       "label": _("EDI Connection"),
                       "description": _("EDI Connection")                   
                   },
                   {
                       "type": "doctype",
                       "name": "EDI File",
                       "label": _("EDI File"),
                       "description": _("EDI File")                   
                   } ,
                   {
                       "type": "doctype",
                       "name": "EDI Sales Report",
                       "label": _("EDI Sales Report"),
                       "description": _("EDI Sales Report")                   
                   },
                   {
                        "type": "report",
                        "name": "EDI Sales Report Overview",
                        "label": _("EDI Sales Report Overview"),
                        "doctype": "EDI Sales Report",
                        "is_query_report": True
                   }
            ]
        }
]
