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
            var user_info = response.message;
            var user_orders = document.querySelector(".user-orders");
            var user_invoices = document.querySelector(".user-invoices");
            
            user_info.forEach(function (info, x) {
				
				if (info.sales_orders) {
					user_orders.innerHTML += `<li class="list-group-item ">${info.sales_orders}</li>`
					
					user_invoices.innerHTML += `<li class="list-group-item ">SINV-TEST</li>`
				} else if (info.sales_invoices) {
					user_invoices.innerHTML += `<li class="list-group-item ">${info.sales_invoices}</li>`
				}
				
			});
		}
	});
}
