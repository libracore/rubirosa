						
document.addEventListener("DOMContentLoaded", function(event) {
    // process command line arguments
    get_arguments();
    
});

function get_arguments() {
	
	var currentUser = frappe.session.user;

    if (currentUser !== "Guest") {
		
		//TEST USER
		//~ currentUser = "toberhem@soer.de";
		load_platform(currentUser);
		
	} else {
		var page_title = document.querySelector(".platform-title");
		var card_deck = document.querySelector(".card-deck");
		var users_only_message = document.querySelector(".users_only_message");

		page_title.style.display = "none"
		card_deck.style.display = "none";
		users_only_message.style.display = "block";
	}
      
}

function load_platform(user) {
	
	frappe.call({
        'method': "rubirosa.rubirosa.assets.get_user_info",
        'args': {
            'user': user,
        },
        'callback': function (response) {
			
            var user_info = response.message.user_info;
            var marketing_material = response.message.marketing_material;
            var so_counter = 0;
            var sinv_counter = 0;
            var user_orders = document.querySelector(".so-accordion");
            var user_invoices = document.querySelector(".sinv-accordion");
            
            if (marketing_material.length > 0) {
				console.log("mmmmm", marketing_material)
				document.querySelector(".no-info-material").style.display = 'none';
				get_marketing_material(marketing_material);
			}
            
            user_info.forEach(function (info, x) {
				if (info.sales_orders) {
					//~ console.log("so", info)
					document.querySelector(".no-info-so").style.display = 'none';
					
					so_counter = so_counter + 1;
					
					var dn_section = "";
					if (Array.isArray(info.delivery_notes)) {
						info.delivery_notes.forEach(function (dn, x) {
							dn_section += `<li><a href="/api/method/frappe.utils.print_format.download_pdf?doctype=Delivery Note&name=${dn}&format=rubirosa Delivery Note&no_letterhead=0&_lang=de" target="_blank" style="font-weight: bold; color: #36414c !important; ">${dn}</a></li>`;
						});
					}
					
					user_orders.innerHTML += `
						<div class="card orders" >
							<div class="card-header so-li" data-toggle="collapse" data-target="#${info.sales_orders}" aria-expanded="true" aria-controls="collapseOne" id="heading${info.sales_orders}" onclick="handle_click(this)">
								<h5 class="mb-0 so-header">
									<i class="fa fa-circle fa-1" aria-hidden="true" style="${info.delivery_status == 'Fully Delivered' ? 'font-size: 12px; color: #98d85b;' : (info.delivery_status === 'Partly Delivered' ? 'font-size: 12px; color: #ffb65c;' : 'font-size: 12px; color: red;')}"></i>
									<button class="btn btn-link so-li-button" >
										 ${info.sales_orders} <br>
										 <p class="key-date">${info.date}</p>
									</button>
								</h5>
							</div>

							<div id="${info.sales_orders}" class="collapse" aria-labelledby="heading{info.sales_orders}" data-parent="#accordion">
								<div class="card-body so-body">
									Delivery Date: <br> <p style="font-weight: bold;"> ${info.delivery_date}</p> <br> 
									Delivery Status: <br> <p style="font-weight: bold;">${info.delivery_status} (${info.per_delivered}%)</p> <br>
									${info.delivery_status !== "Not Delivered" ? 'Delivery Notes: <br> <ul class="delivery-ul ' + info.sales_orders + '">' + dn_section + ' </ul> <br>' : ''}
									<button class="more-info">
										<a href="/api/method/frappe.utils.print_format.download_pdf?doctype=Sales Order&name=${info.sales_orders}&format=rubirosa Sales Order&no_letterhead=0&_lang=de" target="_blank"> More </a>
									</button>
								</div>
							</div>
						</div>
					`;
					
				} else if (info.sales_invoices) {
					document.querySelector(".no-info-sinv").style.display = 'none';
					
					sinv_counter = sinv_counter + 1;
					user_invoices.innerHTML += `
						<div class="card invoices" >
							<div class="card-header so-li" data-toggle="collapse" data-target="#${info.sales_invoices}" aria-expanded="true" aria-controls="collapseOne" id="heading${info.sales_invoices}" onclick="handle_click(this)">
								<h5 class="mb-0 so-header">
									<i class="fa fa-circle fa-1" aria-hidden="true" style="${info.status == 'Paid' ? 'font-size: 12px; color: #98d85b;' : (info.status === 'Return' ? 'font-size: 12px; color: #b8c2cc;' : 'font-size: 12px; color: red;')}"></i>
									<button class="btn btn-link so-li-button" >
										 ${info.sales_invoices}<br>
										 <p class="key-date">${info.date}</p>
									</button>
								</h5>
							</div>

							<div id="${info.sales_invoices}" class="collapse" aria-labelledby="heading${info.sales_invoices}" data-parent="#accordionTwo">
								<div class="card-body so-body">
									Payment Due Date: <br> <p style="font-weight: bold;"> ${info.due_date}</p> <br> Delivery Status: <br> <p style="font-weight: bold;">${info.status}</p> <br>
									<button class="more-info" >
										<a href="/api/method/frappe.utils.print_format.download_pdf?doctype=Sales Invoice&name=${info.sales_invoices}&format=rubirosa Sales Invoice (consolidated)&no_letterhead=0&_lang=de" target="_blank"> More </a>
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

function handle_click(e) {
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

var total_marketing_material;
function get_marketing_material(mm) {
	
	var materialli = document.querySelector(".material");
	materialli.innerHTML = "";
	
	// Amount of Marketing Material shown 
	var maxMaterialsToShow = 10;
	var mm_counter = 0;
	total_marketing_material = mm.length;
	
	mm.forEach(function (material, x) {
		if (material.image) {
			if (mm_counter < maxMaterialsToShow) {
				mm_counter = mm_counter + 1;
				materialli.innerHTML += `<li class="list-group-item marketingli" style="display:block; "><img class='marketingImage' src="${material.image}" onclick="image_click('${material.attachment_urls}')"/> <br> <p class="image-title">${ material.season ? material.season : 'Rubirosa' } - ${material.item_code ? material.item_code.split("-")[0] : ""}</p> <p class="image-text">${material.content ? material.content : '' }</p></li>`;
			} else {
				materialli.innerHTML += `<li class="list-group-item marketingli" style="display:none; "><img class='marketingImage' src="${material.image}" onclick="image_click('${material.attachment_urls}')"/> <br> <p class="image-title">${ material.season ? material.season : 'Rubirosa' } - ${material.item_code ? material.item_code.split("-")[0] : ""}</p> <p class="image-text">${material.content ? material.content : '' }</p></li>`;
			}
		}
	});
	
	if (mm_counter < total_marketing_material) {
		materialli.innerHTML += `<li class="list-group-item marketingli" style="text-align: center !important; "><button class="more-info" style="width: 100% !important; " onclick="load_more()">More</button></li>`
	}	
}

function image_click(attachments) {
	var image_urls = attachments.split(",");
	var user_orders = document.querySelector(".carousel-inner");
	var popUpDiv = document.getElementById("modal");
	var firstImage = true; 
	user_orders.innerHTML = "";
	
	image_urls.forEach(function (image, x) {
		var isActive = firstImage ? "active" : "";
		user_orders.innerHTML += `
			<div class="carousel-item ${isActive}">
				<img class="d-block w-100" src="${image}" >
			</div>`;
		// After the first image, set the flag to false
		firstImage = false;
	});
	
	popUpDiv.style.display = "block";
}

function pop_up_cancel() {
	var popUpDiv = document.getElementById("modal");
    popUpDiv.style.display = "none";
}

var showAllMaterials = true;

function see_all() {
	document.querySelector(".no-info-material").style.display = 'none';
	var icon = document.querySelector('.seeAll');
	icon.classList.toggle('seeAllActive');
	
	if (showAllMaterials) {
		frappe.call({
			'method': "rubirosa.rubirosa.assets.get_marketing_material",
			'args': {
			},
			'callback': function (response) {
				var all_marketing_material = response.message;
				get_marketing_material(all_marketing_material);
			}
		});
		showAllMaterials = false;
	} else {
		var user = frappe.session.user; //"toberhem@soer.de";  
        load_platform(user);
        showAllMaterials = true;
	}
}


function load_more() {
    // Find all hidden and shown marketingli elements
    var hiddenMaterials = document.querySelectorAll('.marketingli[style*="display:none"]');
	var mm_counter = document.querySelectorAll('.marketingli[style*="display:block"]').length;
	
    // Display the next 2 hidden m materials
    for (var i = 0; i < Math.min(2, hiddenMaterials.length); i++) {
        hiddenMaterials[i].style.display = 'block';
        mm_counter++; 
    }
    
    // Check if there are more materials to load
    if ((mm_counter == total_marketing_material) || (total_marketing_material - mm_counter == hiddenMaterials.length )) {
        // No more materials to load, hide the "More" button
        document.querySelector('.more-info').style.display = 'none';
    }
}
