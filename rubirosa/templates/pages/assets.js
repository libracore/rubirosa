						
document.addEventListener("DOMContentLoaded", function(event) {
    // process command line arguments
    get_arguments();
    
});

function get_arguments() {
	
	var currentUser = frappe.session.user;

    if (currentUser !== "Guest") {
		
		//TEST USER
		currentUser = "toberhem@soer.de";
		
		loadPlatform(currentUser);
	} else {
		var page_title = document.querySelector(".platform-title");
		var card_deck = document.querySelector(".card-deck");
		var users_only_message = document.querySelector(".users_only_message");

		page_title.style.display = "none"
		card_deck.style.display = "none";
		users_only_message.style.display = "block";
	}
      
}

function loadPlatform(user) {
	console.log("loadPlatform", user);
	
	frappe.call({
        'method': "rubirosa.rubirosa.assets.get_user_info",
        'args': {
            user: user,
        },
        'callback': function (response) {
			
            var user_info = response.message.user_info;
            var marketing_material = response.message.marketing_material;
            var so_counter = 0;
            var sinv_counter = 0;
            var user_orders = document.querySelector(".user-orders");
            var user_invoices = document.querySelector(".user-invoices");
            
            get_marketing_material(marketing_material);
            
            user_info.forEach(function (info, x) {
				
				if (info.sales_orders) {
					
					so_counter = so_counter + 1;
					user_orders.innerHTML += `<li class="list-group-item so-li">${info.sales_orders}</li>`;
					
				} else if (info.sales_invoices) {
					
					sinv_counter = sinv_counter + 1;
					user_invoices.innerHTML += `<li class="list-group-item sinv-li"> <a href="/api/method/erpnextswiss.erpnextswiss.guest_print.get_pdf_as_guest?doctype=Sales Invoice&name=${info.sales_invoices}&format=rubirosa Sales Invoice (consolidated)&no_letterhead=0" target="_blank" class="">${info.sales_invoices}</a></li>`;
					
				}
				
			});
		}
	});
}

function get_marketing_material(mm) {
			
	// List to store unique seasons
	var unique_seasons = [];
	var mm_counter = 0;
	var materialli = document.querySelector(".material");
		
	mm.forEach(function (material, x) {
			
		if (!unique_seasons.includes(material.season)) {
					
			unique_seasons.push(material.season);
			console.log("unique_seasons", unique_seasons)
			if (material.image) {
				mm_counter = mm_counter + 1;
				materialli.innerHTML += `<li class="list-group-item marketingli"><img class='marketingImage' src="${material.image}"/></li>`;
				console.log("material", materialli)
				}
		}
	});
			

	
}
