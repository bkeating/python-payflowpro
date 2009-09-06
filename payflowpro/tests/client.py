r"""
>>> from payflowpro.classes import (CreditCard, Amount, Profile, 
...                                 Address, Tracking, Response, CustomerInfo)
>>> from payflowpro.client import PayflowProClient, find_classes_in_list, find_class_in_list

>>> PARTNER_ID = None
>>> VENDOR_ID = None
>>> USERNAME = None
>>> PASSWORD = None

>>> client = PayflowProClient(partner=PARTNER_ID,
...                           vendor=VENDOR_ID,
...                           username=USERNAME,
...                           password=PASSWORD)

>>> credit_card = CreditCard(acct=5555555555554444, expdate="1212")

>>> responses, unconsumed_data = client.sale(credit_card, 
...                                         Amount(amt=15, currency="AUD"),
...                                         extras=[Address(street="24285 Elm", zip="00382")])

>>> responses, unconsumed_data = client.authorization(credit_card, Amount(amt=13, currency="AUD"))

>>> transaction_id = responses[0].pnref

>>> responses, unconsumed_data = client.capture(transaction_id)

>>> client_inquiry = client.inquiry(original_pnref=transaction_id, extras=[Tracking(verbosity='M')])[0]
    
>>> profile = Profile(profilename='test_profile_002',
...                             start='07282008',
...                             term=0,
...                             payperiod='WEEK',            
...                             desc="I'm just testing..."),

>>> responses, unconsumed_data = client.profile_add(profile=profile, credit_card=credit_card, amount=Amount(amt=30.00))

>>> responses, unconsumed_data = client.profile_modify(profile_id='RT0000000002', extras=[Profile(optionaltrx='S', optionaltrxamt=12.00),
...                                                     Address(street="123 Somewhere St", city='Sydney', state='NSW', zip="2060"),
...                                                     CustomerInfo(custcode='8675', email='test@example.com', firstname='Joe', lastname='Bloggs'),
...                                                     Tracking(comment1="Order #43",)])

>>> results, unconsumed_data = client.profile_inquiry(profile_id='RT0000000001', payment_history_only=True)
>>> recurring_payments = results[-1]

>>> responses, unconsumed_data = client.profile_inquiry(profile_id='RT0000000001')

>>> address = find_class_in_list(Address, responses)

>>> results, unconsumed_data = client.profile_cancel(profile_id='RT0000000001')

>>> results, unconsumed_data = client.profile_reactivate(profile_id='RT0000000001', extras=[Profile(start="07282008")])
"""

if __name__=="__main__":
    import doctest
    doctest.testmod()
    