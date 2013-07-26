r"""
>>> from payflowpro.classes import CreditCard, Amount, Profile, Address, \
...                                 ShippingAddress, Tracking, Response, \
...                                 CustomerInfo
>>> from payflowpro.client import PayflowProClient, find_classes_in_list, \
...                                 find_class_in_list

>>> # DO NOT FORGET TO CHANGE THESE!
>>> PARTNER_ID = "paypal"
>>> VENDOR_ID = "foobar"
>>> USERNAME = "foobar"
>>> PASSWORD = "password123"

>>> # Setup the client object.
>>> client = PayflowProClient(partner=PARTNER_ID, vendor=VENDOR_ID, 
...                             username=USERNAME, password=PASSWORD)

>>> # Here's a VISA Credit Card for testing purposes.
>>> credit_card = CreditCard(acct=4111111111111111, expdate="0114")


>>> # Let's do a quick sale, charging the account immediately.
>>> responses, unconsumed_data = client.sale(
...     credit_card, 
...     Amount(amt=15, currency="USD"),
...     extras=[Address(street="2842 Magnolia St.", zip="94608")])


>>> # Now let's do an Authorization, making sure the Card on file has
>>> # sufficient funds. This is unrelated to the client.sale() issued above.
>>> responses, unconsumed_data = client.authorization(
...     credit_card, Amount(amt=13, currency="USD"))

>>> # If the authorization worked, we'll have a transaction ID...
>>> transaction_id = responses[0].pnref

>>> # We can now capture the amount authorization
>>> responses, unconsumed_data = client.capture(transaction_id)

>>> # Or we can void it. This is common when doing $1 Authorizations.
>>> responses, unconsumed_data = client.void(transaction_id)

>>> # With a transaction ID in hand, We can make inquiries.
>>> client_inquiry = client.inquiry(
...     original_pnref=transaction_id, extras=[Tracking(verbosity='M')])[0]

>>> # Next, We'll setup a Billing profile...
>>> profile = Profile(profilename='test_profile_002', start='05242012',
...                     term=0, payperiod='WEEK', desc="I'm just testing...")

>>> # Let's add the profile to Payflo Pro's Recurring Billing module. This pro-
>>> # file will be charged $30 every week starting on May 24th 2012.
>>> responses, unconsumed_data = client.profile_add(
...     profile=profile, credit_card=credit_card, amount=Amount(amt=30.00))

>>> # Modifying an existing profile is easy. Here we add a Sales transaction
>>> # for $12.00 (unrelated to recurring charges) along with some additional
>>> # information to help explain the profile.
>>> responses, unconsumed_data = client.profile_modify(
...     profile_id='RT0000000002', extras=[
...         Profile(optionaltrx='S', optionaltrxamt=12.00),
...         Address(street="123 Somewhere St", city='Oakland', state='CA', 
...             zip="94608"),
...         CustomerInfo(custcode='8675', email='test@example.com', 
...             firstname='Joe', lastname='Bloggs'),
...         Tracking(comment1="Order #43",comment2="Submitted by doctest.",)])

>>> # Here is another example with a shipping address, new credit card and 
>>> # without the optional charge.
>>> new_acct = 5105105105105100
>>> new_expdate = 0215
>>> new_cvc = 456
>>> responses, unconsumed_data = client.profile_modify(
...     profile_id='RT0000000002', extras=[
...         Profile(profilename="Joe Bloggs", start=052413,),
...         CreditCard(acct=new_acct,expdate=new_expdate,cvv2=new_cvc,),
...         ShippingAddress(shiptostreet="123 Main St.", shiptocity="Oakland",
...             shiptofirstname="Joe", shiptolastname="Bloggs",
...             shiptostate="CA", shiptocountry="US", shiptozip="94123"),
...         CustomerInfo(email='test@example.com', 
...             firstname='Joe', lastname='Bloggs'),
...         Tracking(comment1="Order #44",comment2="Submitted by doctest.",)])

>>> # Grab a recurring profile's billing history.
>>> results, unconsumed_data = client.profile_inquiry(
...     profile_id='RT0000000001', payment_history_only=True)
>>> recurring_payments = results[-1]


>>> # Inquiry a Recurring Profile by ID...
>>> responses, unconsumed_data = client.profile_inquiry(
...     profile_id='RT0000000001')

>>> # Display the Address associated with the profile.
>>> address = find_class_in_list(Address, responses)

>>> # You can grab other classes too...
>>> info    = find_class_in_list(CustomerInfo, responses)
>>> profile = find_class_in_list(Profile, responses)
>>> cc_info = find_class_in_list(CreditCard, responses)

>>> # You can cancel a Recurring Profile. Some call it "freezing". NOTE: If
>>> # PayPal themselves "cancel" an account, it's dead. You cannot reactivate.
>>> results, unconsumed_data = client.profile_cancel(
...     profile_id='RT0000000001')

>>> # Reactive a user/application canceled Recurring Profile and specify a new
>>> # start date.
>>> results, unconsumed_data = client.profile_reactivate(
...     profile_id='RT0000000001', extras=[Profile(start="07282008")])
"""

if __name__=="__main__":
    import doctest
    doctest.testmod()
    
