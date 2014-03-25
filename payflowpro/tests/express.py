r"""
>>> from payflowpro.classes import Amount, SetPaypal, GetPaypal, DoPaypal
>>> from payflowpro.client import PayflowProClient
>>> from decimal import Decimal

>>> # DO NOT FORGET TO CHANGE THESE!
>>> creds = dict(
...    partner='PayPal',
...    vendor='foo',
...    username='bar',
...    password='password123')

>>> client = PayflowProClient(**creds)

>>> amt = Amount(amt=Decimal('44.00'), freightamt=Decimal('4.00'), currency='USD')
>>> setpp = SetPaypal(returnurl='https://127.0.0.1:8000/shop/confirm/', cancelurl='https://127.0.0.1:8000/shop/cart/')

>>> # first step set express transaction and recieve a token
>>> resps, unconsumed = client.set_checkout(setpp, amt)
>>> # verify transaction was accpepted and we have a token
>>> # token changes every time so just check the first 3 chars which are static
>>> print resps[0]["result"], resps[1]["token"][:3]
0 EC-
>>> token = resps[1]["token"]

>>> # second step is skipped (redirect to paypal)
>>> # it isn't implemented in paypal sandbox
>>> # HTTP 302 to url = client.redirect + token

>>> # third step get buyer info
>>> getpp = GetPaypal(token=token)
>>> resps, unconsumed = client.get_checkout(getpp)
>>> # verify we got 7 response classes, our token, and static payerid
>>> print len(resps), resps[1]["token"]==token, resps[2]["payerid"]=='1234567890123'
7 True True

>>> # final step to finalize the transaction
>>> dopp = DoPaypal(token=token, payerid=resps[2]["payerid"])
>>> resps, unconsumed = client.do_checkout(dopp, amt)
>>> # verify transaction was a success and we have pnref and ppref
>>> print resps[0]["result"]=='0', len(resps[0]["pnref"]), len(resps[3]['ppref'])
True 12 17
"""

if __name__=="__main__":
    import doctest
    doctest.testmod()
