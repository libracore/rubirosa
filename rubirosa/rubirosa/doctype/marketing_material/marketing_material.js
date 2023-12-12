// Copyright (c) 2023, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Marketing Material', {
    refresh: function(frm) {
        // Display only items whose variants end with "420"
        frm.fields_dict['item_code'].get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                    ['Item', 'item_code', 'like', '%-420']
                ]
            };
        };
        //Push Notification Item 
        frm.add_custom_button(__("Push Notifications Item"), function() {
            push_notifications(frm, "Item");
            
        });
        
        //Push Notification Sales Season 
        frm.add_custom_button(__("Push Notifications Sales Season "), function() {
            push_notifications(frm, "Season");
            
        });
    }
});

function push_notifications(frm, reason) {
    frappe.call({
        'method': "push_notifications",
        'doc': frm.doc,
        'args': {
            'reason': reason,
            'item': frm.doc.item_code,
            'season': frm.doc.season
        },
        'callback': function (response) {
            var contacts = response.message;
            
            window.location.href = "mailto:" + frm.doc.owner + "?subject=New Marketing Material&bcc=" + contacts.join(',');

        }
    });
}
