"""
Copyright 2008 Online Agility (www.onlineagility.com)

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
from copy import deepcopy
import re

class ValidationError(Exception):
    def __init__(self, message):
        self.message = message

class Field(object):
    def __init__(self, required=False, default=None):
        self.required = required
        self.default =  default
        self._value = None

    def get_value(self):
        return self._value or self.default
    
    def clean(self, value):
        return value
    
    def set_value(self, value):
        self._value = self.clean(value)
        
    value = property(get_value, set_value)
    
    def __get__(self):
        return self.value

    def is_valid(self):
        if self.required and not self.value:
            raise ValidationError("Required Field")
            
class CreditCardField(Field):
    def clean(self, value):
        if isinstance(value, basestring):
            return re.sub(r'\s', '', value)
        else:
            return value
                
class DeclarativeFieldsMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['base_fields'] = dict([(field_name, attrs.pop(field_name)) for field_name, obj in attrs.items() if isinstance(obj, Field)])
        new_class = super(DeclarativeFieldsMetaclass, cls).__new__(cls, name, bases, attrs)
        return new_class            
            
class PayflowProObjectBase(object):
    """
    A Python class to represent Payflow request and response objects, that has 
    attributes matching a set of required and optional attribute names.
    
    Objects can be initialised from the generated class in one of four ways:
    
    # Provide attributes as positional arguments, in the order the fields 
    # were defined
    >>> cc = CreditCard(5555555555554444, "1212")

    # Provide required attributes as positional arguments, and optional 
    # atttributes as keyword arguments
    >>> cc = CreditCard(5555555555554444, expdate="0110", cvv2="123")

    # Provide all attributes as keyword arguments
    >>> cc = CreditCard(acct=5555555555554444, expdate="0110", cvv2="123")
    
    # Provide some or all of the attributes as a data dictionary
    >>> cc = CreditCard(data=dict(acct=5555555555554444, expdate="0110", cvv2="123"))

    A class instance is only valid if it contains attribute values for all of the 
    required attributes. You can check the completeness of a class instance by
    calling the `errors` method.
    """    
    def __init__(self, data={}, **kwargs):
        self._errors = None
        # base_fields is a class variable rather than instance variable, 
        # deepcopy to allow modification of an instance's fields.
        self.fields = deepcopy(self.base_fields)
        
        for field, value in data.items():
            self.fields[field].value = value
        
        for name, value in kwargs.items():
            if not name in self.fields:
                raise TypeError("__init__() got an unexpected keyword argument '%s'" % name)
            self.fields[name].value = value
    
    def _get_data(self):
        return dict([(field, obj.value) for field, obj in self.fields.items() if obj.value])
    data = property(_get_data)
    
    def __getitem__(self, key):
        return self.data[key]
        
    def __setitem__(self, key, value):
        self.fields[key].value = value
        
    def __getattr__(self, attr):
        if attr != 'fields' and ('fields' in self.__dict__) and (attr in self.__dict__['fields']):
            return self.__dict__['fields'][attr].value
        else:
            return self.__dict__[attr]
    
    def __setattr__(self, attr, value):
        if ('fields' in self.__dict__) and (attr in self.__dict__['fields']):
            self.__dict__['fields'][attr].value = value
        else:
            self.__dict__[attr] = value            
    
    def __str__(self):
        return "%s: %s" % (self.__class__.__name__, self.data)
    
    def _get_required_fields(self):
        return [field for field, obj in self.fields.items() if obj.required]
    required = property(_get_required_fields)
    
    def _get_optional_fields(self):
        return [field for field, obj in self.fields.items() if not obj.required]
    optional = property(_get_optional_fields)
    
    def _get_errors(self):
        if not self._errors:
            self.is_valid()
        return self._errors
    errors = property(_get_errors)
    
    def is_valid(self):
        self._errors = {}
        for name, field in self.fields.items():
            try:
                field.is_valid()
            except ValidationError, e:
                self._errors[name] = e.message                
    
class PayflowProObject(PayflowProObjectBase):
    __metaclass__ = DeclarativeFieldsMetaclass

class CreditCard(PayflowProObject):
    acct = CreditCardField(required=True)
    expdate = Field()
    cvv2 = Field()
    tender = Field(default="C")

class CreditCardPresent(PayflowProObject):
    swipe = Field(required=True)
    cvv2 = Field()
    tender = Field(default="C")

class Amount(PayflowProObject):
    amt = Field(required=True)
    currency = Field()
    dutyamt = Field()
    freightamt = Field()
    taxamt = Field()
    
class Tracking(PayflowProObject):
    comment1 = Field()
    comment2 = Field()
    verbosity = Field()
    
class TimeBounds(PayflowProObject):
    starttime = Field()
    endtime = Field()

class Address(PayflowProObject):
    street = Field(required=True)
    zip = Field()
    city = Field()
    billtocountry = Field()
    state = Field()
    country = Field()
    companyname = Field()

class ShippingAddress(PayflowProObject):
    shiptostreet = Field(required=True)
    shiptocity = Field()
    shiptofirstname = Field()
    shiptomiddlename = Field()
    shiptolastname = Field()
    shiptostate = Field()
    shiptocountry = Field()
    shiptozip = Field()

class CustomerInfo(PayflowProObject):
    custcode = Field()
    email = Field()
    firstname = Field()
    name = Field()
    middlename = Field()
    lastname = Field()
    phonenum = Field()

class PurchaseInfo(PayflowProObject):
    ponum = Field()

class Profile(PayflowProObject):
    profilename = Field(required=True)
    start = Field(required=True)
    term = Field(required=True)
    payperiod = Field(required=True)
    maxfailpayments = Field()
    desc = Field()
    optionaltrx = Field()
    optionaltrxamt = Field()
    status = Field()
    paymentsleft = Field()
    nextpayment = Field()
    end = Field()
    aggregateamt = Field()
    aggregateoptionalamt = Field()
    numfailpayments = Field()
    retrynumdays = Field()
    
class Response(PayflowProObject):
    result = Field(required=True)
    respmsg = Field()
    pnref = Field()
    cvv2match = Field()
    proccvv2 = Field()
    authcode = Field()
    paymenttype = Field()
    correlationid = Field()
    balamt = Field()
    prefpsmsg = Field()
    postfpsmsg = Field()
    cardsecure = Field()
    origresult = Field()
    custref = Field()
    origpnref = Field()

class ProfileResponse(PayflowProObject):
    profileid = Field(required=True)
    rpref = Field(required=True)
    trxpnref = Field()
    trxresult = Field()
    trxrespmsg = Field()

class VerboseResponse(PayflowProObject):
    hostcode = Field()
    resptext = Field()
    procardsecure = Field()
    addlmsgs = Field()
    transstate = Field()
    date_to_settle = Field()
    batchid = Field()
    amexid = Field()
    amexposdata = Field()
    visacardlevel = Field()
    settle_date = Field()

class AddressVerificationResponse(PayflowProObject):
    avsaddr = Field()
    avszip = Field()
    iavs = Field()
    procavs = Field()

class RecurringPayment(PayflowProObject):
    p_result = Field(required=True)
    p_pnref = Field(required=True)
    p_transtate = Field(required=True)
    p_tender = Field(required=True)
    p_transtime = Field(required=True)
    p_amt = Field(required=True)    

# Recurring Payments are a special kind of response, which may
# comprise a number of payment records.
class RecurringPayments(object):
    def __init__(self, payments):
        self.payments = payments
    
    def __len__(self):
        return len(self.payments)
    
    def __iter__(self):
        return self.payments.__iter__()


# Parse results dictionary into a set of PayflowProObjects
def parse_parameters(payflowpro_response_data):
    """
    Parses a set of Payflow Pro response parameter name and value pairs into 
    a list of PayflowProObjects, and returns a tuple containing the object
    list and a dictionary containing any unconsumed data. 
    
    The first item in the object list will always be the Response object, and
    the RecurringPayments object (if any) will be last.

    The presence of any unconsumed data in the resulting dictionary probably
    indicates an error or oversight in the PayflowProObject definitions.
    """
    def build_class(klass, unconsumed_data):
        known_att_names_set = set(klass.base_fields.keys())
        available_atts_set = known_att_names_set.intersection(unconsumed_data)
        if available_atts_set:
            available_atts = dict()
            for name in available_atts_set:
                available_atts[name] = unconsumed_data[name]
                del unconsumed_data[name]                    
            return klass(**available_atts)
        return None

    unconsumed_data = payflowpro_response_data.copy()

    # Parse the response data first
    response = build_class(Response, unconsumed_data)
    result_objects = [response]

    if int(response.result) != 0:
        # Error response
        return (result_objects, unconsumed_data,)
    
    # Parse the remaining data
    for klass in object.__class__.__subclasses__(PayflowProObject):
        obj = build_class(klass, unconsumed_data)
        if obj:
            result_objects.append(obj)
    
    # Special handling of RecurringPayments
    recurpaycount = 1
    payments = []
    while ("p_result%d" % recurpaycount) in unconsumed_data:
        payments.append(RecurringPayment(
            p_result = unconsumed_data.pop("p_result%d" % recurpaycount),
            p_pnref = unconsumed_data.pop("p_pnref%d" % recurpaycount),
            p_transtate = unconsumed_data.pop("p_transtate%d" % recurpaycount),
            p_tender = unconsumed_data.pop("p_tender%d" % recurpaycount),
            p_transtime = unconsumed_data.pop("p_transtime%d" % recurpaycount),
            p_amt = unconsumed_data.pop("p_amt%d" % recurpaycount)))
        recurpaycount += 1
    if payments:
        result_objects.append(RecurringPayments(payments=payments))
        
    return (result_objects, unconsumed_data,)
