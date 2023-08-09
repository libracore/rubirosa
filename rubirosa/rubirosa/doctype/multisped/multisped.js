// Copyright (c) 2023, libracore and contributors
// For license information, please see license.txt


frappe.ui.form.on('Multisped', {
	refresh(frm) {
		frm.add_custom_button(__("Get Data"),  () => get_data(frm))
	}
})

function get_data(frm) {
    //~ frappe.call({
        //~ 'method': "rubirosa.rubirosa.doctype.multisped.multisped.get_data",
        //~ 'args': {
                //~ "doc": frm.doc.name
            //~ },
        //~ 'callback': function (response) {
            //~ var res = response.message;
            //~ console.log("res", res);
//~ }
//~ })
// generate intrastat csv file
    frappe.call({
        method: 'rubirosa.rubirosa.doctype.multisped.multisped.generate_transfer_file',
        args: {
        },
        callback: function(r) {
            if (r.message) {
                // prepare the xml file for download
                var res = r.message.content;
                var today = new Date();
                download("Multisped WMS - ARTIKELSTAMMSATZ " + today.getFullYear() + "-" + (today.getMonth() + 1) + ".csv", res);
                //~ var today = new Date();
                //~ download("intrastat_" + today.getFullYear() + "-" + (today.getMonth() + 1) + ".csv", r.message.content);
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
