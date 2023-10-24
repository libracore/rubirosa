						
document.addEventListener("DOMContentLoaded", function(event) {
    // process command line arguments
    get_arguments();
    
});

function get_arguments() {
	
	var currentUser = frappe.session.user;

    if (currentUser !== "Guest") {
		
		//TEST USER
		currentUser = "davestoll@bluewin.ch";
		
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
            var user_orders = document.querySelector(".so-accordion");
            var user_invoices = document.querySelector(".sinv-accordion");
            
            get_marketing_material(marketing_material);
            
            user_info.forEach(function (info, x) {
				
				if (info.sales_orders) {
					so_counter = so_counter + 1;
					user_orders.innerHTML += `
						<div class="card orders" >
							<div class="card-header so-li" data-toggle="collapse" data-target="#${info.sales_orders}" aria-expanded="true" aria-controls="collapseOne" id="heading${info.sales_orders}" onclick="handleClick(this)">
								<h5 class="mb-0 so-header">
									<i class="fa fa-circle fa-1" aria-hidden="true" style="${info.delivery_status == 'Fully Delivered' ? 'font-size: 12px; color: #98d85b;' : 'font-size: 12px; color: red;'}"></i>
									<button class="btn btn-link so-li-button" >
										 ${info.sales_orders}
									</button>
								</h5>
							</div>

							<div id="${info.sales_orders}" class="collapse" aria-labelledby="heading{info.sales_orders}" data-parent="#accordion">
								<div class="card-body so-body">
									Delivery Date: <br> <p style="font-weight: bold;"> ${info.delivery_date}</p> <br> Delivery Status: <br> <p style="font-weight: bold;">${info.delivery_status}</p> <br>
									<button class="more-info">
										<a href="/api/method/frappe.utils.print_format.download_pdf?doctype=Sales Order&name=${info.sales_orders}&format=rubirosa Sales Order&no_letterhead=0&_lang=de" target="_blank"> More </a>
									</button>
								</div>
							</div>
						</div>
					`;
					
				} else if (info.sales_invoices) {
					
					sinv_counter = sinv_counter + 1;
					user_invoices.innerHTML += `
						<div class="card invoices" >
							<div class="card-header so-li" data-toggle="collapse" data-target="#${info.sales_invoices}" aria-expanded="true" aria-controls="collapseOne" id="heading${info.sales_invoices}" onclick="handleClick(this)">
								<h5 class="mb-0 so-header">
									<i class="fa fa-circle fa-1" aria-hidden="true" style="${info.status == 'Paid' ? 'font-size: 12px; color: #98d85b;' : 'font-size: 12px; color: red;'}"></i>
									<button class="btn btn-link so-li-button" >
										 ${info.sales_invoices}
									</button>
								</h5>
							</div>

							<div id="${info.sales_invoices}" class="collapse" aria-labelledby="heading${info.sales_invoices}" data-parent="#accordionTwo">
								<div class="card-body so-body">
									Payment Due Date: <br> <p style="font-weight: bold;"> ${info.due_date}</p> <br> Delivery Status: <br> <p style="font-weight: bold;">${info.status}</p> <br>
									<button class="more-info" >
										<a href="/api/method/frappe.utils.print_format.download_pdf?doctype=Sales Invoice&name=${info.sales_invoices}&format=rubirosa Sales Invoice&no_letterhead=0&_lang=de" target="_blank"> More </a>
									</button>
								</div>
							</div>
						</div>
					`;
					
				}
				
			});
		}
	});
}

function handleClick(e) {
	var hasCardActiveClass = e.classList.contains('card-active');
	var elementsWithCardActive = document.querySelectorAll('.card-active');
	elementsWithCardActive.forEach(element => {
		
        if (element !== e && element.parentNode.classList[1] === e.parentNode.classList[1]) {
            element.classList.remove('card-active');
        }
    });
    
    if (!hasCardActiveClass) {
        e.classList.add('card-active');
    } else {
		e.classList.remove('card-active');
	}
}

function get_marketing_material(mm) {
	//~ console.log("mm", mm)	
	// List of displayed Marketing Materials
	var mm_list = [];
	var unique_seasons = [];
	var templates = [];
	var mm_counter = 0;
	var materialli = document.querySelector(".material");
		
	mm.forEach(function (material, x) {
		//~ console.log("material", material)
		if (!mm_list.includes(material.name)) {	
			mm_list.push(material.name);
			if (material.image) {
				mm_counter = mm_counter + 1;
				materialli.innerHTML += `<li class="list-group-item marketingli"><img class='marketingImage' src="${material.image}"/> <br> <p class="image-title">${ material.season ? material.season : 'Rubirosa' } - ${material.item_code ? material.item_code : ""}</p> <p class="image-text">${material.content ? material.content : '' }</p></li>`;
			} else {
				materialli.innerHTML += `<li class="list-group-item marketingli"><p class="image-title">${ material.season ? material.season : 'Rubirosa' } - ${material.item_code}</p> <p class="image-text">${material.content ? material.content : '' }</p></li>`;
			}
		} 
	});
			
}
