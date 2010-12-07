# PayPal's Payflow Pro Python Client 

``python-payflowpro`` (or simply ``payflowpro`` within the Python environment) 
provides an interface to the PayPal Payflow Pro API (HTTPS Interface) making it 
easy for you to collect and manage payments within your python-based 
applications.

This project is a fork of [James Murty](jamurty@gmail.com) & 
[John D'Agostino](john.dagostino@gmail.com)'s python-payflowpro project hosted 
on [Google Code](http://code.google.com/p/python-payflowpro/). 

__Specifically, It allows you to:__

*  Submit Sales Transactions
*  Submit Authorization & Delayed Capture Transactions
*  Security Code (CVV, CVC2, CVV2) & Address Verification (Requires 
Verification module. Additional costs apply.)
*  Create Recurring Billing Profiles (Requires Recurring Billing module. 
Additional costs apply.)
*  Modify & Reactivate Recurring Billing Profiles
*  Display payment history of a Recurring Billing Profile
*  Cancel A Recurring Billing Profile (aka 'Freezing')
*  Inquiry Transactions (One-time & Recurring Billing Profile)

__Payment Methods Supported (TENDER\_TYPES)__

* Automated clearinghouse
* Credit card
* Pinless debit
* Telecheck
* PayPal

__Transactions Types Supported (TRANSACTION\_TYPES)__

* Sale transaction
* Credit
* Authorization
* Delayed Capture
* Void
* Voice Authorization
* Inquiry
* Duplicate transaction
* Recurring *(Optional. Requires Recurring Billing module. 
Additional costs apply.)*

## Requirements

*   Python 2.5+
*   [PayPal "Payflow" Services Account](https://registration.paypal.com/) on 
    PayPal.com

The recurring billing functionality of this library requires the PayflowPro 
account to have the Recurring Billing module activated (additional costs 
apply). Likewise with the Security Code & Address Verification module. Unless 
you have the appropriate modules enabled within your Paypal Payflow Pro 
Account (This is set via the [Paypal Manager](https://manager.paypal.com)), 
passing Street Addresses and Security Codes will not be ran through 
verification.

## Installation

You can install python-payflowpro one of three ways:

* run ``python setup.py install`` within the ``python-payflowpro`` directory
* ``ln -s /path/to/python-payflowpro/payflowpro /path/to/site-packages/``
* ``pip install -e git://github.com/bkeating/python-payflowpro.git#egg=django_payflowpro``

Each approach gives you the same result. You can test your installation by
starting an interactive prompt:

    $ python
    >>> import payflowpro
    >>> payflowpro.VERSION
    (0, 3, 'pre')

## Usage

Refer to the ``client.py`` file in the ``tests`` subdirectory for example usage 
of the client.

To run the tests you will have to edit the file and set the following variables 
with a valid Payflow Pro Account.

* ``PARTNER_ID``
* ``VENDOR_ID``
* ``USERNAME``
* ``PASSWORD``
