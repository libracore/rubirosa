frappe.pages['customer-overview'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Kunden Overview'),
        single_column: true
    });

    frappe.customer_overview.make(page);
    frappe.customer_overview.run();

    // add the application reference
    frappe.breadcrumbs.add("rubirosa");
}

frappe.customer_overview = {
    start: 0,
    make: function(page) {
        var me = frappe.customer_overview;
        me.page = page;
        me.body = $('<div></div>').appendTo(me.page.main);
        var data = "";
        $(frappe.render_template('customer_overview', data)).appendTo(me.body);

        // load leaflet
        var cssId = 'leafletCss'; 
        if (!document.getElementById(cssId))
        {
            var head  = document.getElementsByTagName('head')[0];
            var link  = document.createElement('link');
            link.id   = cssId;
            link.rel  = 'stylesheet';
            link.type = 'text/css';
            link.href = '/assets/rubirosa/css/leaflet.css';
            link.media = 'all';
            head.appendChild(link);
        }

        frappe.customer_overview.start_wait();

    },
    run: function() {
        frappe.customer_overview.render_map();
    },
    render_map: function(address=null) {
        // fetch object
        var customer_name = frappe.customer_overview.get_arguments();
        var gps_lat = 46.984338787480695;
        var gps_long = 8.411922818855178;
        var initial_zoom = 13;
        var geo = null;
        var radius = 0.1;
        if ((!customer_name) && (!address)) {
            radius = 50;    // no object: load full map
        }

        // prepare various icons
        var green_icon = new L.Icon({'iconUrl': '/assets/rubirosa/images/marker-icon-green.png'});
        var red_icon = new L.Icon({'iconUrl': '/assets/rubirosa/images/marker-icon-red.png'});
        var grey_icon = new L.Icon({'iconUrl': '/assets/rubirosa/images/marker-icon-grey.png'});
        var blue_icon = new L.Icon({'iconUrl': '/assets/rubirosa/images/marker-icon.png'});

        // create map     
        document.getElementById('map-container').innerHTML = "<div id='map' style='width: 100%; height: 800px;'></div>";
        var map = L.map('map').setView([gps_lat, gps_long], initial_zoom);
        // create layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
        // hack: issue a resize event
        window.dispatchEvent(new Event('resize')); 

        document.getElementById("overlay-text").innerHTML = "<p>Objekte suchen...</p>";

        frappe.call({
            'method': 'rubirosa.rubirosa.utils.get_geographic_environment',
            'args': { 
                'customer_name': customer_name,
                'radius': radius,
                'address': address
            },
            'callback': function(r) {
                if (r.message) {
                    geo = r.message;
                    gps_lat = geo.gps_lat;
                    gps_long = geo.gps_long;
                    map.panTo(new L.LatLng(gps_lat, gps_long));
                }

                document.getElementById("overlay-text").innerHTML = "<p>" + geo.environment.length + " Objekte platzieren...</p>";

                // add marker for the reference object
                L.marker([gps_lat, gps_long], {'icon': red_icon}).addTo(map)
                    .bindPopup(get_popup_str(customer_name));
                // add other markers
                if (geo) {
                    console.log(geo);
                    for (var i = 0; i < geo.environment.length; i++) {

                        // set icon color
                        var icon = blue_icon
                        
                        L.marker([geo.environment[i].gps_lat, geo.environment[i].gps_long],
                            {'icon': icon}).addTo(map)
                            .bindPopup(get_popup_str(geo.environment[i].customer));

                    }
                }

                // hack: issue a resize event
                window.dispatchEvent(new Event('resize')); 
                frappe.customer_overview.end_wait();
                frappe.show_alert(geo.environment.length + " Objekte geladen");
            }
        }); 
    },
    get_arguments: function() {
        var arguments = window.location.toString().split("?");
        if (!arguments[arguments.length - 1].startsWith("http")) {
            var args_raw = arguments[arguments.length - 1].split("&");
            var args = {};
            args_raw.forEach(function (arg) {
                var kv = arg.split("=");
                if (kv.length > 1) {
                    args[kv[0]] = kv[1];
                }
            });
            if (args['customer']) {
                return args['customer'];
            }
        } 
    },
    start_wait: function() {
        document.getElementById("waitingScreen").style.display = "block";
    },
    end_wait: function() {
        document.getElementById("waitingScreen").style.display = "none";
    }
}

function get_popup_str(customer_name) {
    html = "<b><a href=\"/desk#Form/Customer/" 
        + (customer_name || "rubirosa") + "\" target=\"_blank\">" 
        + (customer_name || "rubirosa") + "</a></b>";

    return html;
}