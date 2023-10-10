						
document.addEventListener("DOMContentLoaded", function(event) {
    // process command line arguments
    get_arguments();
    
    //Pop Up
    var uploadInput = document.getElementById('upload');
    uploadInput.addEventListener('change', function () {
        readURL(this);
    });
    
});

function get_arguments() {
	
	var currentUser = frappe.session.user;

    if (currentUser !== "Guest") {
		
		//TEST USER
		currentUser = "jakehollinger@gmail.com";
		
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
			
	// List of displayed Marketing Materials
	var mm_list = [];
	var unique_seasons = [];
	var templates = [];
	var mm_counter = 0;
	var materialli = document.querySelector(".material");
		
	mm.forEach(function (material, x) {
			console.log("material", material.item_code)
		if (!mm_list.includes(material.name)) {	
			console.log("variant_of", material.variant_of)
			mm_list.push(material.name);
			console.log("mm_list", mm_list)
			if (material.image) {
				mm_counter = mm_counter + 1;
				materialli.innerHTML += `<li class="list-group-item marketingli"><img class='marketingImage' src="${material.image}"/> <br> <p class="image-title">${material.season} - ${material.item_code}</p> <p class="image-text">${material.content}</p></li>`;
			}
		} 
	});
			
}


function uploadMedia() {
	var popUpDiv = document.getElementById("modal");
	popUpDiv.style.display = "block";

}

function popUpConfirm() {
	var fileName = document.getElementById( 'upload-label' ).textContent;
	var content = document.getElementById('textarea').value;
	
	frappe.call({
        "method": 'rubirosa.rubirosa.assets.create_marketing_material',
        "args": {
            "file_name": fileName,
            "content": content
        },
        "callback": function (response) {
            if (response.message) {
                console.log('Marketing Material created successfully:', response.message);
            } 
        }
    });
    popUpCancel();
}


function popUpCancel() {
	var infoArea = document.getElementById( 'upload-label' );
	var textarea = document.getElementById('textarea');
	var imageDisplay = document.getElementById('imageResult');
	var popUpDiv = document.getElementById("modal");
	
	imageDisplay.src = "";
	textarea.value = "";
	infoArea.textContent = "Choose a File";
    popUpDiv.style.display = "none";
}


function readURL(input) {

	showFileName( input );
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            document.getElementById('imageResult').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}


/*  HOW UPLOADED IMAGE NAME*/
function showFileName( input ) {
	var infoArea = document.getElementById( 'upload-label' );
	var fileName = input.files[0].name;
	infoArea.textContent =  fileName;
}
