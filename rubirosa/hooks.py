# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "rubirosa"
app_title = "Rubirosa"
app_publisher = "libracore"
app_description = "rubirosa business applications"
app_icon = "octicon octicon-star"
app_color = "black"
app_email = "info@libracore.com"
app_license = "AGPL"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/rubirosa/css/rubirosa.css"
# app_include_js = "/assets/rubirosa/js/rubirosa.js"

# include js, css files in header of web template
# web_include_css = "/assets/rubirosa/css/rubirosa.css"
# web_include_js = "/assets/rubirosa/js/rubirosa.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Customer" : "public/js/customer.js",
    "Item" : "public/js/item.js",
    "Delivery Note": "public/js/delivery_note.js",
    "Purchase Order": "public/js/purchase_order.js", 
    "Purchase Receipt": ["public/js/xlsx.full.min.js",
        "public/js/purchase_receipt.js"
    ],
    "Monthly Distribution": "public/js/monthly_distribution.js",
}
doctype_list_js = {
    "Item" : "public/js/item_list.js"
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# adding Jinja environments
jenv = {
    "methods": [
        "get_sales_season_matrix:rubirosa.rubirosa.print.get_sales_season_matrix"
    ]
}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "rubirosa.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "rubirosa.install.before_install"
# after_install = "rubirosa.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "rubirosa.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"rubirosa.tasks.all"
# 	],
# 	"daily": [
# 		"rubirosa.rubirosa.msdirect.write_latest_items"
# 	],
# 	"hourly": [
# 		"rubirosa.tasks.hourly"
# 	],
# 	"weekly": [
# 		"rubirosa.tasks.weekly"
# 	]
# 	"monthly": [
# 		"rubirosa.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "rubirosa.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "rubirosa.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "rubirosa.task.get_dashboard_data"
# }

