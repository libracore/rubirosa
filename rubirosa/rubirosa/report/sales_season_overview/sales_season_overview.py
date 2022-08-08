# Copyright (c) 2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from rubirosa.rubirosa.print import get_sales_season_matrix

def execute(filters=None):
    filters = frappe._dict(filters or {})
    
    data = get_data(filters)
    columns = get_columns(data)
    
    output = []
    size_sums = {}
    
    for k,v in data["matrix"].items():
        _output = {
            'model': k
        }
        _sum = 0
        for sk,sv in v.items():
            _output[sk] = sv
            _sum += sv
            if sk not in size_sums:
                size_sums[sk] = sv
            else:
                size_sums[sk] += sv
                
        _output['total'] = _sum
        
        output.append(_output)
    
    # sort
    output = sorted(output, key=lambda d: d['model'])
    
    # add size sums
    _sum = 0
    _output = {'model': "Total"}
    for sk,sv in size_sums.items():
        _output[sk] = sv
        _sum += sv
        if sk not in size_sums:
            size_sums[sk] = sv
        else:
            size_sums[sk] += sv
    _output['total'] = _sum
    output.append(_output)
    
    return columns, output
    
def get_columns(data):
    columns = [
        {"label": _("Model"), "fieldname": "model", "fieldtype": "Data", "width": 150}
    ]
    
    for s in data['sizes']:
        columns.append(
            {"label": s, "fieldname": s, "fieldtype": "Float", "width": 70},
        )
    
    columns.append(
        {"label": _("Total"), "fieldname": "total", "fieldtype": "Float", "width": 70},
    )
    return columns
    
def get_data(filters):
    
    data = get_sales_season_matrix(filters.monthly_distribution, filters.territory)
        
    return data
