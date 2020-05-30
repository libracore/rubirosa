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
                   }
            ]
        },
        {
            "label": _("Integrations"),
            "icon": "fa fa-bank",
            "items": [
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
				   }
            ]
        }
]
