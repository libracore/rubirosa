// Copyright (c) 2023, libracore and contributors
// For license information, please see license.txt


frappe.ui.form.on('Multisped Settings', {
	refresh(frm) {
		console.log("Multisped Settings")
		frm.add_custom_button(__("Get Item Dataaa"),  () => get_data(frm))
	}
});

function get_data(frm) {

// generate intrastat csv file
    frappe.call({
        method: 'rubirosa.rubirosa.doctype.multisped_settings.multisped_settings.generate_items_transfer_file',
        args: {
        },
        callback: function(r) {
			console.log("r", r)
            if (r.message) {
                // prepare the xml file for download
                
                var csv = r.message.content;
                var today = new Date();
                download("Multisped WMS - ARTIKELSTAMMSATZ " + today.getFullYear() + "-" + (today.getMonth() + 1) + ".csv", csv);
            } 
        }
    });
}

function download(filename, content) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:application/octet-stream;charset=utf-8,' + encodeURIComponent(content));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}
