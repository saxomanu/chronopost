#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
In order to use this lib, you have to call the method 'get_shipping_label'
with the right arguments. To know which keys to send to this method read these lists :
- required fields
- fields

"""



from datetime import datetime
import re
from suds.client import Client, WebFault
from .label_helper import AbstractLabel
from .exception_helper import (
    InvalidSequence,
    InvalidWeight,
    InvalidSize,
    InvalidType,
    InvalidMissingField,
    InvalidZipCode,
    InvalidCountry,
    InvalidDate,
    InvalidCode,
    InvalidValue,
    InvalidValueNotInList,
)


WEBSERVICE_URL = 'https://ws.chronopost.fr/shipping-cxf/ShippingServiceWS?wsdl'

ESD_MODEL = {
    "retrievalDateTime":         {'max_size': 17},
    "closingDateTime":           {'max_size': 17},
    "specificInstructions":      {'max_size': 255},
    "height":                    {'required': True},
    "width":                     {'required': True},
    "length":                    {'required': True},
    "shipperCarriesCode":        {'max_size': 38},
    "shipperBuildingFloor":      {'max_size': 32},
    "shipperServiceDirection":   {'max_size': 32},
}


HEADER_MODEL = {
    "accountNumber":    {'required': True, 'max_size': 8},
    "subAccount":       {'max_size': 3},
}


ADDRESS_MODEL = {
    "civility":     {'in': ['E', 'L', 'M']},
    "name":         {'required': True, 'max_size': 100},
    "name2":        {'required': True, 'max_size': 100},
    "street":       {'required': True, 'max_size': 38},
    "street2":      {'max_size': 38},
    "zip":          {'required': True, 'max_size': 9},
    "city":         {'required': True, 'max_size': 50},
    "country_code": {'required': True, 'max_size': 2},
    "phone":        {'max_size': 17},
    "mobile":       {'max_size': 17},
    "email":        {'max_size': 80},
    "alert":        {}, #FIXME
}


REF_MODEL = {
    "shipperRef":             {'required': True, 'max_size': 35},
    "recipientRef":           {'required': True},
    "customerSkybillNumber":  {'max_size': 38},
}

SKYBILL_MODEL = {
    "productCode":       {'required': True},
    "shipDate":          {'max_size': 38},
    "shipHour":          {'required': True, 'max_size': 9},
    "weight":            {'required': True, 'type': float},
    "weightUnit":        {'required': True},
    "insuredValue":      {'type': int},
    "insuredCurrency":   {'max_size': 17},
    "codValue":          {'type': int},
    "codCurrency":       {'max_size': 80},
    "customsValue":      {'type': int},
    "customsCurrency":   {'max_size': 80},
    "service":           {'max_size': 1},
    "objectType":        {'max_size': 80},
    "content1":          {'max_size': 80},
    "content2":          {'max_size': 80},
    "content3":          {'max_size': 80},
    "content4":          {'max_size': 80},
    "content5":          {'max_size': 80},
}


def is_digit(s):
    return re.search("[^0-9]", s) is None


class Chronopost(AbstractLabel):
    _client = None


    def __init__(self):
        self._client = Client(WEBSERVICE_URL)


    def _send_request(self, request, *args):
        """ Wrapper for API requests

        :param request: callback for API request
        :param **kwargs: params forwarded to the callback

        """
        res = {}
        try:
            res['value'] = request(*args)
            res['success'] = True
        except WebFault as e:
            res['success'] = False
            res['errors'] = [e[0]]
        except Exception as e:
            # if authentification error
            #if isinstance(e[0], tuple) and e[0][0] == 401:
                #raise e[0][0]
            raise e
        return res


    def _prepare_skybillparams(self, mode):
        skybillparams_obj = self._client.factory.create('skybillParamsValue')
        valid_values = ['PDF', 'PPR', 'SPD', 'THE', 'ZPL', 'XML']
        if mode in valid_values:
            skybillparams_obj['mode'] = mode
        else:
            raise InvalidValueNotInList(
                "The printing mode must be in %s" % valid_values)
        return skybillparams_obj


    def _check_password(self, password):
        if is_digit(password) is False:
            raise InvalidType(
                "Only digit chars are authorised for 'account' '%s'"
                % account)
        if len(str(password)) != 6:
            raise InvalidSize(
                "The password have to contain 6 characters")
        return password


    def _prepare_skybill(self, info):
        self.check_model(info, SKYBILL_MODEL, 'skybill')
        skybill_obj = self._client.factory.create('skybillValue')
        #for key in info.keys():
         #  skybill_obj[key] = info[key] 
        skybill_obj = info.copy()
        skybill_obj['evtCode'] = 'DC'
        return skybill_obj


    def _prepare_ref(self, info):
        self.check_model(info, REF_MODEL, 'ref')
        ref_obj = self._client.factory.create('refValue')
        #for key in info.keys():
         #  ref_obj[key] = info[key] 
        ref_obj = info.copy()
        return ref_obj


    def _prepare_esd(self, info):
        self.check_model(info, ESD_MODEL, 'esd')
        esd_obj = self._client.factory.create('esdValue')
        #esd_obj['retrievalDateTime'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        #esd_obj['closingDateTime'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        esd_obj = info.copy()
        return esd_obj



    def _prepare_customer_address(self, address):
        customer_model = ADDRESS_MODEL.copy()
        customer_model['civility'] = {'in': ['E', 'L', 'M'], 'required': True}
        customer_model['print_as_sender'] = {'in': ['Y', 'N']}
        print "****", address, "***"
        self.check_model(address, customer_model, 'address')
        elements = {
            'customerCivility': 'civility',
            'customerName': 'name',
            'customerName2': 'name2',
            'customerAdress1': 'street',
            'customerAdress2': 'street2',
            'customerZipCode': 'zip',
            'customerCity': 'city',
            'customerCountry': 'country_code',
            'customerCountryName': 'country_name',
            'customerContactName': 'contact_name',
            'customerEmail': 'email',
            'customerPhone': 'phone',
            'customerMobilePhone': 'mobile',
            'customerPreAlert': 'alert',
            'printAsSender': 'print_as_sender'
        }
        customer = self._client.factory.create('customerValue')
        return customer, elements


    def _prepare_shipper_address(self, address):
        shipper_model = ADDRESS_MODEL.copy()
        shipper_model['civility'] = {'in': ['E', 'L', 'M'], 'required': True}
        self.check_model(address, shipper_model, 'address')
        elements = {
            'shipperCivility': 'civility',
            'shipperName': 'name',
            'shipperName2': 'name2',
            'shipperAdress1': 'street',
            'shipperAdress2': 'street2',
            'shipperZipCode': 'zip',
            'shipperCity': 'city',
            'shipperCountry': 'country_code',
            'shipperCountryName': 'country_name',
            'shipperContactName': False,
            'shipperEmail': 'email',
            'shipperPhone': 'phone',
            'shipperMobilePhone': 'mobile',
            'shipperPreAlert': 'alert',
        }
        shipper = self._client.factory.create('shipperValue')
        return shipper, elements


    def _prepare_recipient_address(self, address):
        print "address", address
        self.check_model(address, ADDRESS_MODEL, 'address')
        elements = {
            'recipientName': 'name',
            'recipientName2': 'name2',
            'recipientAdress1': 'street',
            'recipientAdress2': 'street2',
            'recipientZipCode': 'zip',
            'recipientCity': 'city',
            'recipientCountry': 'country_code',
            'recipientCountryName': 'country_name',
            'recipientContactName': 'contact_name',
            'recipientEmail': 'email',
            'recipientPhone': 'phone',
            'recipientMobilePhone': 'mobile',
            'recipientPreAlert': 'alert',
        }
        recipient = self._client.factory.create('recipientValue')
        return recipient, elements


    def _prepare_address(self, values, info_type):
        if info_type == 'recipient':
            obj, elements = self._prepare_recipient_address(values)
        if info_type == 'shipper':
            obj, elements = self._prepare_shipper_address(values)
        if info_type == 'customer':
            obj, elements = self._prepare_customer_address(values)
        if obj and elements and values:
            for elm, elm_v in elements.items():
                obj[elm] = ''
                if elm_v in values:
                    obj[elm] = values[elm_v]
        return obj


    def _check_account(self, account):
        if is_digit(account) is False:
            raise InvalidType(
                "Only digit chars are authorised for 'account' '%s'"
                % account)
        return account


    def _prepare_header(self, vals):
        self.check_model(vals, HEADER_MODEL, 'header')
        self._check_account(vals['accountNumber'])
        header = self._client.factory.create('headerValue')
        header['idEmit'] = 'CHRFR'
        header['accountNumber'] = vals['accountNumber']
        if vals.get('subAccount', False):
            self._check_account(vals['subAccount'])
            header['subAccount'] = vals['subAccount']
        return header


    def get_shipping_label(self, recipient, shipper, header, ref, skybill,
                 password, esd=None, mode=False, customer = None):
        """
        Call Chronopost 'shipping' web service and return the label in binary.
        Params TODO
        """
        if not customer:
            customer = shipper.copy()
        header_obj = self._prepare_header(header.copy())
        recipient_obj = self._prepare_address(recipient.copy(), 'recipient')
        shipper_obj = self._prepare_address(shipper.copy(), 'shipper')
        customer_obj = self._prepare_address(customer.copy(), 'customer')

        if esd:
            esd_obj = self._prepare_esd(esd.copy())
        else:   
            esd_obj = self._client.factory.create('esdValue')

        ref_obj = self._prepare_ref(ref.copy())
        skybill_obj = self._prepare_skybill(skybill.copy())

        password = self._check_password(password)
        if mode:
            skybillparams_obj = self._prepare_skybillparams(mode)
        else:
            skybillparams_obj = self._client.factory.create('skybillParamsValue')
        #test = self._client.service.shipping(esd, head, shiping, customer, recipient, ref, sky, bill, '255562')
        request = self._client.service.shipping
        response = self._send_request(request, esd_obj, header_obj, shipper_obj,
                                      customer_obj, recipient_obj, ref_obj, 
                                      skybill_obj, skybillparams_obj, password)
        return response



