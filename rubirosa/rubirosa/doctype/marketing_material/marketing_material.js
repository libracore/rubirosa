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
        //Push Function 
        frm.add_custom_button(__("Push Notifications"), function() {
			push_notifications(frm);
			
        });
    }
});


function push_notifications(frm) {
	frappe.call({
		'method': "rubirosa.rubirosa.doctype.marketing_material.marketing_material.push_notifications",
		'args': {
			'item': frm.doc.item_code,
			'season': frm.doc.season
		},
		'callback': function (response) {
			var contacts = response.message;
			
			window.location.href = "mailto:" + frm.doc.owner + "?subject=New Marketin Material&bcc=" + contacts.join(',');

		}
	});
}
