"""
Copyright 2008 Online Agility (www.onlineagility.com)
Copyright 2009 John D'Agostino (http://www.mercurycomplex.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import sys, time, re, types, logging

from urllib2 import Request, urlopen, urlparse

from classes import (CreditCard, Amount, Profile, 
                     Address, Tracking, Response, parse_parameters)


"""
TENDER_TYPES:
    'A', # Automated clearinghouse 
    'C', # Credit card 
    'D', # Pinless debit 
    'K', # Telecheck 
    'P', # PayPal


TRANSACTION_TYPES:
    'S', # Sale transaction 
    'C', # Credit 
    'A', # Authorization 
    'D', # Delayed Capture 
    'V', # Void 
    'F', # Voice Authorization 
    'I', # Inquiry 
    'N', # Duplicate transaction 
    'R', # Recurring
"""

class CurrentTimeIdGenerator(object):
    def id(self):
        """
        Returns the current time in milliseconds as an integer.
        """
        return int(time.time() * 1000) # Current time in milliseconds


class PayflowProClient(object):
    """    
    Payflow Pro client for API version 4 (also known as the HTTPS 
    API interface)
    """
    URL_BASE_TEST = 'https://pilot-payflowpro.paypal.com'
    URL_BASE_LIVE = 'https://payflowpro.paypal.com'
    HOSTPORT = 443
    API_VERSION = '4'
    CLIENT_IDENTIFIER = 'python-payflowpro'
    MAX_RETRY_COUNT = 5 # How many times to retry failed logins or rate limited operations
    
    def __init__(self, partner, vendor, username, password, timeout_secs=45,
        idgenerator=CurrentTimeIdGenerator(), url_base=URL_BASE_TEST):
        
        self.partner = partner
        self.vendor = vendor
        self.username = username
        self.password = password
        self.timeout = timeout_secs
        self.url_base = url_base
        self.idgenerator = idgenerator
        self.log = logging.getLogger('payflow_pro')
        
    def _build_parmlist(self, parameters):
        """
        Converts a dictionary of name and value pairs into a 
        PARMLIST string value acceptable to the Payflow Pro API.
        """
        args = []
        for key, value in parameters.items():
            if not value is None:
                # We always use the explicit-length keyname format, to reduce the chance
                # of requests failing due to unusual characters in parameter values.
                key = '%s[%d]' % (key.upper(), len(str(value))) 
                args.append('%s=%s' % (key, value))
        args.sort()
        parmlist = '&'.join(args)        
        return parmlist
    
    def _parse_parmlist(self, parmlist):
        """
        Parses a PARMLIST string into a dictionary of name and value 
        pairs. The parsing is complicated by the following:
        
         - parameter keynames may or may not include a length 
           specification
         - delimiter characters (=, &) may appear inside parameter
           values, provided the parameter has an explicit length.
        
        For example, the following parmlist values are possible:
        
          A=B&C=D
          A[1]=B&C[1]=D
          A=B&C[1]=D
          A[3]=B&B&C[1]=D  (Here, the value of A is "B&B")
          A[1]=B&C[3]=D=7  (Here, the value of C is "D=7")
        """
        parmlist = "&" + parmlist
        name_re = re.compile(r'\&([A-Z0-9_]+)(\[\d+\])?=')
        
        results = {}
        offset = 0
        match = name_re.search(parmlist, offset)
        while match:
            name, len_suffix = match.groups()
            offset = match.end()
            if len_suffix:
                val_len = int(len_suffix[1:-1])
            else:
                next_match = name_re.search(parmlist, offset)
                if next_match:
                    val_len = next_match.start() - match.end()
                else:
                    # At end of parmlist
                    val_len = len(parmlist) - match.end()
            value = parmlist[match.end() : match.end() + val_len]
            results[name.lower()] = value
                                    
            match = name_re.search(parmlist, offset)
        return results        

    def _do_request(self, request_id, parameters={}):
        """
        """
        if request_id is None:
            # Generate a new request identifier using the class' default generator
            request_id = self.idgenerator.id()
        
        req_params = dict(parameters)
        req_params.update(dict(
            partner = self.partner,
            vendor = self.vendor,
            user = self.username,
            pwd = self.password,            
        ))
        
        parmlist = self._build_parmlist(req_params)
        
        headers = {
            'Host': urlparse.urlsplit(self.url_base)[1],
            'X-VPS-REQUEST-ID': str(request_id),
            'X-VPS-CLIENT-TIMEOUT': str(self.timeout), # Doc says to do this
            'X-VPS-Timeout': str(self.timeout), # Example says to do this
            'X-VPS-INTEGRATION-PRODUCT': self.CLIENT_IDENTIFIER,
            'X-VPS-INTEGRATION-VERSION': self.API_VERSION,
            'X-VPS-VIT-OS-NAME': sys.platform,
            'Connection': 'close',
            'Content-Type': 'text/namevalue',            
            }
        self.log.debug(u"Request Headers: %s" % headers)
            
        try_count = 0
        results = None
        while (results is None and try_count < self.MAX_RETRY_COUNT):
            try:
                try_count += 1
                
                request = Request(
                    url = self.url_base, 
                    data = parmlist, 
                    headers = headers)
                    
                response = urlopen(request)
                result_parmlist = response.read()
                response.close()
                
                self.log.debug(u"Result text: %s" % result_parmlist)
                
                results = self._parse_parmlist(result_parmlist)
            except Exception, e:
                if try_count < self.MAX_RETRY_COUNT:
                    self.log.warn(u"API request attempt %s of %s failed" % (try_count, self.MAX_RETRY_COUNT), e)
                else:
                    self.log.exception(u"Final API request failed", e)
                    raise e
        
        self.log.debug(u"Parsed PARMLIST: %s" % results)
        
        # Parse results dictionary into a set of PayflowProObjects
        result_objects, unconsumed_data = parse_parameters(results)
        self.log.debug(u"Result parsed objects: %s" % result_objects)
        self.log.debug(u"Unconsumed Data: %s" % unconsumed_data)
        return (result_objects, unconsumed_data)
    
    
    ##### Implementations of standard transactions #####
    
    def sale(self, credit_card, amount, request_id=None, extras=[]):        
        params = dict(trxtype = "S")
        for item in [credit_card, amount] + extras:
            params.update(item.data)
        return self._do_request(request_id, params)

    def authorization(self, credit_card, amount, request_id=None, extras=[]):        
        params = dict(trxtype = "A")
        for item in [credit_card, amount] + extras:
            params.update(item.data)
        return self._do_request(request_id, params)

    def capture(self, auth_pnref, request_id=None, extras=[]):        
        params = dict(trxtype = "D", origid = auth_pnref)
        for item in extras:
            params.update(item.data)
        return self._do_request(request_id, params)

    def voice_authorization(self, voice_auth_code, credit_card, amount, request_id=None, extras=[]):
        params = dict(trxtype = "F", authcode = voice_auth_code)
        for item in [credit_card, amount] + extras:
            params.update(item.data)
        return self._do_request(request_id, params)

    def credit_referenced(self, original_pnref, request_id=None, extras=[]):
        params = dict(trxtype = "C", origid = original_pnref)
        for item in extras:
            params.update(item.data)
        return self._do_request(request_id, params)

    def credit_unreferenced(self, credit_card, amount, request_id=None, extras=[]):
        params = dict(trxtype = "C")
        for item in [credit_card, amount] + extras:
            params.update(item.data)
        return self._do_request(request_id, params)

    def void(self, original_pnref, request_id=None, extras=[]):
        params = dict(trxtype = "V", origid = original_pnref)
        for item in extras:
            params.update(item.data)
        return self._do_request(request_id, params)

    def inquiry(self, original_pnref=None, customer_ref=None, request_id=None, extras=[]):
        params = dict(trxtype = "I", origid = original_pnref, custref = customer_ref)
        if original_pnref is None and customer_ref is None:
            raise TypeError("An inquiry requires one of the 'original_pnref' or 'customer_ref' arguments")
        if not original_pnref is None and not customer_ref is None:
            raise TypeError("An inquiry requires only one of the 'original_pnref' or 'customer_ref' arguments, not both")
        for item in extras:
            params.update(item.data)
        return self._do_request(request_id, params)

    def reference_transaction(self, transaction_type, original_pnref, amount, request_id=None, extras=[]):
        params = dict(trxtype = transaction_type, origid = original_pnref)
        for item in [amount] + extras:
            params.update(item.data)
        return self._do_request(request_id, params)

    ##### Implementations of recurring transactions #####
    
    def profile_add(self, profile, credit_card, amount, request_id=None, extras=[]):
        params = dict(trxtype = 'R', action = 'A')
        for item in [profile, credit_card, amount] + extras:
            params.update(item.data)
        return self._do_request(request_id, params)

    def profile_add_from_transaction(self, original_pnref, request_id=None, extras=[]):
        params = dict(trxtype = 'R', action = 'A', origid = original_pnref)
        for item in extras:
            params.update(item.data)
        return self._do_request(request_id, params)        

    def profile_modify(self, profile_id, request_id=None, extras=[]):
        params = dict(trxtype = 'R', action = 'M', origprofileid = profile_id)
        for item in extras:
            params.update(item.data)
        return self._do_request(request_id, params)        

    def profile_reactivate(self, profile_id, request_id=None, extras=[]):
        params = dict(trxtype = 'R', action = 'R', origprofileid = profile_id)
        for item in extras:
            params.update(item.data)
        return self._do_request(request_id, params)        

    def profile_cancel(self, profile_id, request_id=None, extras=[]):
        params = dict(trxtype = 'R', action = 'C', origprofileid = profile_id)
        for item in extras:
            params.update(item.data)
        return self._do_request(request_id, params)        

    def profile_inquiry(self, profile_id, payment_history_only=False, request_id=None, extras=[]):
        params = dict(trxtype = 'R', action = 'I', origprofileid = profile_id)
        if payment_history_only:
            params['paymenthistory'] = 'Y'
        for item in extras:
            params.update(item.data)
        return self._do_request(request_id, params)        
    
    def profile_pay(self, profile_id, payment_number, request_id=None, extras=[]):
        params = dict(trxtype = 'R', action = 'P', 
            origprofileid = profile_id, paymentnum = payment_number)
        for item in extras:
            params.update(item.data)
        return self._do_request(request_id, params)        


def find_class_in_list(klass, lst):
    """
    Returns the first occurrence of an instance of type `klass` in 
    the given list, or None if no such instance is present.
    """
    filtered = filter(lambda x: x.__class__ == klass, lst)
    if filtered:
        return filtered[0]
    return None

def find_classes_in_list(klasses, lst):
    """
    Returns a tuple containing an entry corresponding to each of
    the requested class types, where the entry is either the first
    object instance of that type or None of no such instances are
    available.
    
    Example Usage:
    
    find_classes_in_list(
        [Address, Response],
        [<classes.Response...>, <classes.Amount...>, <classes.Address...>])
        
    Produces: (<classes.Address...>, <classes.Response...>)            
    """
    if not isinstance(klasses, list):
        klasses = [klasses]
    return tuple(map(lambda klass: find_class_in_list(klass, lst), klasses))
