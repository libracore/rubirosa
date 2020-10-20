# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020, libracore (https://www.libracore.com) and contributors
# For license information, please see license.txt
#
# Test functions for interface module for MS Direct
import msdirect

def test_get_purchase_receipts()
    response = """<?xml version="1.0" encoding="UTF-8"?><e:Envelope xmlns:d="http://www.w3.org/2001/XMLSchema" xmlns:e="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wn1="http://systinet.com/wsdl/com/magicsoftware/magicxpi/msDataHandling/" xmlns:wn2="http://systinet.com/xsd/SchemaTypes/" xmlns:wn0="http://idoox.com/interface" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
    <e:Envelope xmlns:d="http://www.w3.org/2001/XMLSchema" xmlns:e="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wn1="http://systinet.com/wsdl/com/magicsoftware/magicxpi/msDataHandling/" xmlns:wn2="http://systinet.com/xsd/SchemaTypes/" xmlns:wn0="http://idoox.com/interface" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
    <e:Body>
      <wn1:purchaseReceiptResponse>
        <wn1:response i:type="wn1:PurchaseReceiptResponse">
          <wn1:error i:nil="true"/>
          <wn1:messageHeader i:type="wn1:MessageHeader">
            <wn1:clientId i:type="d:string">123</wn1:clientId>
            <wn1:clientName i:type="d:string">123</wn1:clientName>
            <wn1:token i:type="d:string">12345</wn1:token>
          </wn1:messageHeader>
          <wn1:response i:type="wn1:ArrayOfPurchaseReceiptData">
            <wn1:PurchaseReceiptData i:type="wn1:PurchaseReceiptData">
              <wn1:bookingDate i:type="d:date">2020-09-17</wn1:bookingDate>
              <wn1:deliveredQuantity i:type="d:decimal">10.00</wn1:deliveredQuantity>
              <wn1:itemNo i:type="d:string">01/100820/450</wn1:itemNo>
              <wn1:orderDate i:type="d:date">2020-09-17</wn1:orderDate>
              <wn1:orderQuantity i:type="d:decimal">20.00</wn1:orderQuantity>
              <wn1:purchaseOrderLineNo i:type="d:string">1</wn1:purchaseOrderLineNo>
              <wn1:purchaseOrderNo i:type="d:string">PO-00001</wn1:purchaseOrderNo>
              <wn1:unitOfMeasure i:type="d:string">PAA</wn1:unitOfMeasure>
              <wn1:vendorItemNo i:type="d:string"></wn1:vendorItemNo>
              <wn1:vendorName i:type="d:string">Testkreditor von MAPO</wn1:vendorName>
              <wn1:vendorNo i:type="d:string">00000002</wn1:vendorNo>
              <wn1:vendorOrderLineNo i:type="d:string"></wn1:vendorOrderLineNo>
              <wn1:vendorOrderNo i:type="d:string"></wn1:vendorOrderNo>
            </wn1:PurchaseReceiptData>
            <wn1:PurchaseReceiptData i:type="wn1:PurchaseReceiptData">
              <wn1:bookingDate i:type="d:date">2020-09-17</wn1:bookingDate>
              <wn1:deliveredQuantity i:type="d:decimal">15.00</wn1:deliveredQuantity>
              <wn1:itemNo i:type="d:string">01/100802/430</wn1:itemNo>
              <wn1:orderDate i:type="d:date">2020-09-17</wn1:orderDate>
              <wn1:orderQuantity i:type="d:decimal">15.00</wn1:orderQuantity>
              <wn1:purchaseOrderLineNo i:type="d:string">1</wn1:purchaseOrderLineNo>
              <wn1:purchaseOrderNo i:type="d:string">PO-00002</wn1:purchaseOrderNo>
              <wn1:unitOfMeasure i:type="d:string">PAA</wn1:unitOfMeasure>
              <wn1:vendorItemNo i:type="d:string">556655</wn1:vendorItemNo>
              <wn1:vendorName i:type="d:string">Stark Industires</wn1:vendorName>
              <wn1:vendorNo i:type="d:string">456</wn1:vendorNo>
              <wn1:vendorOrderLineNo i:type="d:string">1</wn1:vendorOrderLineNo>
              <wn1:vendorOrderNo i:type="d:string">5566</wn1:vendorOrderNo>
            </wn1:PurchaseReceiptData>
            <wn1:PurchaseReceiptData i:type="wn1:PurchaseReceiptData">
              <wn1:bookingDate i:type="d:date">2020-09-17</wn1:bookingDate>
              <wn1:deliveredQuantity i:type="d:decimal">200.00</wn1:deliveredQuantity>
              <wn1:itemNo i:type="d:string">01/100802/400</wn1:itemNo>
              <wn1:orderDate i:type="d:date">2020-09-17</wn1:orderDate>
              <wn1:orderQuantity i:type="d:decimal">200.00</wn1:orderQuantity>
              <wn1:purchaseOrderLineNo i:type="d:string">2</wn1:purchaseOrderLineNo>
              <wn1:purchaseOrderNo i:type="d:string">PO-00002</wn1:purchaseOrderNo>
              <wn1:unitOfMeasure i:type="d:string">STK</wn1:unitOfMeasure>
              <wn1:vendorItemNo i:type="d:string">556655</wn1:vendorItemNo>
              <wn1:vendorName i:type="d:string">Stark Industires</wn1:vendorName>
              <wn1:vendorNo i:type="d:string">456</wn1:vendorNo>
              <wn1:vendorOrderLineNo i:type="d:string">1</wn1:vendorOrderLineNo>
              <wn1:vendorOrderNo i:type="d:string">5566</wn1:vendorOrderNo>
            </wn1:PurchaseReceiptData>
          </wn1:response>
        </wn1:response>
      </wn1:purchaseReceiptResponse>
    </e:Body></e:Envelope>"""
    result = msdirect.parse_purchase_orders(response)
    print(result)
