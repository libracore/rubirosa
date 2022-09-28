// Copyright (c) 2020-2022, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Order Overview"] = {
    "filters": [
        {
            "fieldname":"sales_season",
            "label": __("Sales Season"),
            "fieldtype": "Link",
            "options": "Monthly Distribution",
            "reqd": 1
        },
        {
            "fieldname":"territory",
            "label": __("Territory"),
            "fieldtype": "Link",
            "options": "Territory"
        }
    ],
    "onload": (report) => {
        report.page.add_inner_button(__('Create Purchase Order'), function () {
            create_purchase_order();
        });
    }
};

function create_purchase_order() {
    // collect sales orders from current view
    sales_orders = []
    for (var i = 0; i < frappe.query_report.data.length; i++) {
        if (frappe.query_report.data[i].sales_order) {
            sales_orders.push({
                'sales_order': frappe.query_report.data[i].sales_order,
                'customer': frappe.query_report.data[i].customer,
                'name': frappe.query_report.data[i].sales_order // (sales_orders.length +1)
            });
        }
    }
    
    // show selection dialog
    var d = new frappe.ui.Dialog({
        'title': __('Select Sales Orders for Purchase Order'),
        'fields': [
            {
                'label': 'Supplier',
                'fieldname': 'supplier',
                'fieldtype': 'Link',
                'options': 'Supplier',
                'reqd': 1
            },
            {
                'label': 'Sales Orders',
                'fieldname': 'section_sales_orders',
                'fieldtype': 'Section Break'
            },
            {
                'label': 'Sales Orders',
                'fieldtype': 'Table',
                'fieldname': 'sales_orders',
                'description': __('Select Sales Orders (remove rows that should not be used)'),
                'fields': [
                    {
                        'fieldtype': 'Read Only',
                        'fieldname': 'sales_order',
                        'label': __('Sales Order'),
                        'in_list_view': 1
                    }, 
                    {
                        'fieldtype': 'Link',
                        'fieldname': 'customer',
                        'options': 'Customer',
                        'reqd': 1,
                        'label': __('Customer'),
                        'in_list_view': 1,
                        'read_only': 1
                    }
                ],
                'data': sales_orders,
                'get_data': () => {
                    return sales_orders
                }
            }
        ],
        'primary_action': function() {
            var data = d.get_values();
            d.hide();
            frappe.call({
                'method': 'rubirosa.rubirosa.report.order_overview.order_overview.create_purchase_order',
                'args': {
                    'sales_orders': data.sales_orders,
                    'supplier': data.supplier
                },
                'freeze': true,
                'freeze_message': __("Creating Purchase Order..."),
                'callback': function(r) {
                    frappe.show_alert( __("Purchase Order created") );
                    frappe.query_report.refresh();
                }
            });
        },
        'primary_action_label': __('Create')
    });
    d.show();
}
