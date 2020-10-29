frappe.ui.form.on("Item", {
    before_save: function(frm) {
      if ((!frm.doc.__islocal) && (frm.doc.is_stock_item) && (frm.doc.barcode) && (frm.doc.barcode.length <= 17)) {
          write_to_msdirect(frm);
      }
});

function write_to_msdirect(frm) {
    // wait for the data to be stored in the database
    sleep(5000).then(() => {
        frappe.call({
    		method: 'rubirosa.rubirosa.msdirect.write_item',
    		args: {
    			'item_code': frm.doc.name
    		},
    		callback: function(r) {
    			frappe.show_alert("Artikel an MS Direct übertragen");
    		}
    	}); 
    });
}

function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}
