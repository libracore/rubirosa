						
document.addEventListener("DOMContentLoaded", function(event) {
    // process command line arguments
    get_arguments();
    
});

function get_arguments() {
	
	var currentUser = frappe.session.user;
	input = document.getElementById("myInput").value = "";

    if (currentUser !== "Guest") {
		load_platform(currentUser);
	} else {
		var page_title = document.querySelector(".platform-intro");
		var card_deck = document.querySelector(".card-deck");
		var users_only_message = document.querySelector(".users_only_message");

		page_title.style.display = "none"
		card_deck.style.display = "none";
		users_only_message.style.display = "block";
	}
      
}

var showAllMaterials = true;
var loadAll = false;
var orders = "";
function load_platform(user) {
	console.log("load", user);
	frappe.call({
        'method': "rubirosa.rubirosa.asset_platform.get_user_info",
        'args': {
            'user': user,
        },
        'callback': function (response) {
			
            var user_info = response.message.user_info;
            var so_counter = 0;
            var sinv_counter = 0;
            var user_orders = document.querySelector(".so-accordion");
            var user_invoices = document.querySelector(".sinv-accordion");
                        
            user_info.forEach(function (info, x) {
				if (info.sales_orders) {
					document.querySelector(".no-info-so").style.display = 'none';
					//~ orders.push(info.sales_orders);
					orders += `${info.sales_orders},`;
					so_counter = so_counter + 1;
					
					var dn_section = "";
					if (Array.isArray(info.delivery_notes)) {
						info.delivery_notes.forEach(function (dn, x) {
							dn_section += `<li><a href="/api/method/frappe.utils.print_format.download_pdf?doctype=Delivery Note&name=${dn}&format=rubirosa Delivery Note&no_letterhead=0&_lang=${info.language}" target="_blank" style="font-weight: bold; color: #36414c !important; ">${dn}</a></li>`;
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
										<a href="/api/method/frappe.utils.print_format.download_pdf?doctype=Sales Order&name=${info.sales_orders}&format=rubirosa Sales Order&no_letterhead=0&_lang=${info.language}" target="_blank"> More </a>
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
										<a href="/api/method/frappe.utils.print_format.download_pdf?doctype=Sales Invoice&name=${info.sales_invoices}&format=rubirosa Sales Invoice (consolidated)&no_letterhead=0&_lang=${info.language}" target="_blank"> More </a>
									</button>
								</div>
							</div>
						</div>
					`;
					
				}
				
			});
			
			see_all();
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
var offset = 20;
function get_marketing_material(mm, clean) {
	
	var materialli = document.querySelector(".material");
	
	// If true, clean the feed to display Images accordingly
	if (clean) {
		materialli.innerHTML = "";
	}
	
	// Remove the moreBtn when adding more Marketing Material
	if (materialli.lastChild) {
        materialli.removeChild(materialli.lastChild);
    }
	
	var mm_counter = 0;
	
	mm.forEach(function (material, x) {
		if (material.image) {
			var copy_section = "";
			if (material.content) {
				copy_section = `<div style="display: flex; justify-content: space-between;"> <p class="image-text" >${material.content ? material.content : '' }</p> <input style="visibility: hidden; width: 0px;" type="text" value="${material.content}" id="myInput${x}"> <button class="fa fa-clone copyBtn" id="copyBtn${x}" onclick="copy_to_clipboard(${x})"></button> </div> `;
			} 
			mm_counter = mm_counter + 1;
			materialli.innerHTML += `<li class="list-group-item marketingli" style="display:block; ">  <div class="image-container"> <img class='marketingImage' src="${material.image}" onclick="image_click('${material.attachment_urls}')"/> ${ material.category ? '<div class="overlay">' + material.category + '</div>' : ''} </div><br> <p class="image-title">${ material.season ? material.season : 'Rubirosa' } - ${material.item_code ? material.item_code.split("-")[0] : ""}</p> ${copy_section}</li>`;
		}
	});
	
	//Setting the exact displayed amount
	offset = materialli.childNodes.length;
	console.log("total_marketing_material", total_marketing_material);
	console.log("offset", offset);

	//if the fetch total_marketing_material is less than the limit that means that there wont be more to showcase 
	if (total_marketing_material > offset) { 
		materialli.innerHTML += `<li class="list-group-item marketingli" style="text-align: center !important; "><button class="more-info" style="width: 100% !important; " onclick="load_more()">More</button></li>`;
	}
}

function copy_to_clipboard(x) {
	// Get the text field
	var copyText = document.getElementById("myInput" + x);
	var copyBtn = document.getElementById("copyBtn" + x);
	
	copyBtn.classList.remove('fa-clone'); 
	copyBtn.classList.add('fa-check'); 
	
	// Select the text field for mobile devices
	copyText.select();
	copyText.setSelectionRange(0, 99999);

	// Copy the text inside the text field
	navigator.clipboard.writeText(copyText.value);
	
	setTimeout(function() {
		copyBtn.classList.remove('fa-check'); 
		copyBtn.classList.add('fa-clone');
	}, 1500);
}

var image_urls = [];
function image_click(attachments) {
	image_urls = attachments.split(",");
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
	
	if (image_urls.length == 1 ) {
		document.querySelector(".carousel-control-prev-icon").style.display = 'none';
		document.querySelector(".carousel-control-next-icon").style.display = 'none';
	} else {
		document.querySelector(".carousel-control-prev-icon").style.display = 'inline-block';
		document.querySelector(".carousel-control-next-icon").style.display = 'inline-block';
	}
}

function download_all() {
	
	image_urls.forEach(link => {
        var anchor = document.createElement('a');
        anchor.href = link;
        anchor.download = link.split('/').pop();
        anchor.click();
        URL.revokeObjectURL(anchor.href);
    });
}

function pop_up_cancel() {
	var popUpDiv = document.getElementById("modal");
    popUpDiv.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.addEventListener('click', function (event) {
	var modal = document.getElementById('modal');
	if (event.target === modal) {
		modal.style.display = 'none';
    }
});

function see_all() {
	document.querySelector(".no-info-material").style.display = 'none';
	document.querySelector(".list-group").style.display = 'block';
	var icon = document.querySelector('.seeAll');
	icon.classList.toggle('seeAllActive');
	
	if (showAllMaterials) {
		frappe.call({
			'method': "rubirosa.rubirosa.asset_platform.get_marketing_material",
			'callback': function (response) {
				var all_marketing_material = response.message;
				total_marketing_material = all_marketing_material[1][0].total_records;
				get_marketing_material(all_marketing_material[0], true);
			}
		});
		
		showAllMaterials = false;
		loadAll = true;
		
	} else {
        
		frappe.call({
			'method': "rubirosa.rubirosa.asset_platform.get_marketing_material",
			'args': { 'orders': orders },
			'callback': function (response) {
				var all_marketing_material = response.message;
				if (all_marketing_material[1] != 0) {
					total_marketing_material = all_marketing_material[1][0].total_records;
					get_marketing_material(all_marketing_material[0], true);
				} else {
					document.querySelector(".no-info-material").style.display = 'block';
					document.querySelector(".list-group").style.display = 'none';
				}
			}
		});
		
        showAllMaterials = true;
        loadAll = false;
	}

}

// Uses the limit and offset to track what has been displayed and calls another batch of 5
function load_more() {
	var limit = 5;
	if (loadAll) {
		frappe.call({
			'method': "rubirosa.rubirosa.asset_platform.get_marketing_material",
			'args': { 'offset': offset, 'limit': limit },
			'callback': function (response) {
				var more_marketing_material = response.message;
				get_marketing_material(more_marketing_material[0]);
			}
		});
	} else {
		frappe.call({
			'method': "rubirosa.rubirosa.asset_platform.get_marketing_material",
			'args': { 'orders': orders, 'offset': offset, 'limit': limit },
			'callback': function (response) {
				var more_marketing_material = response.message;
				get_marketing_material(more_marketing_material[0]);
			}
		});
	}
    
}

// Function to filter materials based on search query
function filterMaddterials() {
    var searchInput = document.getElementById('searchInput').value.trim().toLowerCase();
    var filteredMaterials = marketing_material.filter(function(material) {
        // Check if the search query matches any part of the material content
        return material.content.toLowerCase().includes(searchInput);
    });
    
    // If search input is empty, display all materials
    if (searchInput === "") {
        get_marketing_material(marketing_material, true);
    } else {
        get_marketing_material(filteredMaterials, true);
    }
}

function filterMaterials() {

    var input, filter, ul, li, a, i, txtValue;
    var anyVisibleChildNode = false;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    ul = document.querySelector(".material");
    li = ul.getElementsByTagName("li");

    var loadMoreButton = ul.lastChild;
    loadMoreButton.style.display = 'none'; 

    for (i = 0; i < li.length; i++) {
		if (li[i].children[3]) {
			a = li[i].children[3].children[0];
			txtValue = a.textContent || a.innerText;
			
		} else if (li[i].children[2]) {		
			a = li[i].children[2];
			txtValue = a.textContent || a.innerText;
		}
		
		if (txtValue && txtValue.toUpperCase().indexOf(filter) > -1) {
			li[i].style.display = "block";
		} else {
			li[i].style.display = "none";
		}
		
    }
    
    for (i = 0; i < li.length; i++) {
        var computedStyle = window.getComputedStyle(li[i]);
        if (computedStyle.display !== 'none') {
            anyVisibleChildNode = true;
            break;
        } 
    }
    
    if (!anyVisibleChildNode) {
		document.querySelector(".no-info-material").style.display = 'block';
	} else {
		document.querySelector(".no-info-material").style.display = 'none';
	}
    
    if (input.value == "") {
		loadMoreButton.style.display = 'block';
	}
}
