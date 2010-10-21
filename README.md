# Python Paypal PayflowPro Client

``python-payflowpro`` provides an interface to the PayPal PayflowPro API (HTTPS Interface) 
making it easy for you to collect payments within your python-based applications.

This project is a fork of [James Murty](jamurty@gmail.com) & [John D'Agostino](john.dagostino@gmail.com) python-payflowpro work hosted on [Google Code](http://code.google.com/p/python-payflowpro/).


__Specifically, You can:__

*  Submit Sales Transactions
*  Submit Authorization & Delayed Capture Transactions
*  Security Code (CVV, CVC2, CVV2) & Address Verification (requires Verification module. Additional costs apply.)
*  Create Recurring Billing Profiles (requires Recurring Billing module. Additional costs apply.)
*  Modify & Reactivate Recurring Billing Profiles
*  Display payment history of a Recurring Billing Profile
*  Cancel A Recurring Billing Profile (aka 'Freezing')
*  Inquiry Transactions (One-time & Recurring Billing Profile)


__Payment Methods Supported (TENDER\_TYPES)___

* `` 'A' `` = *Automated clearinghouse*
* `` 'C' `` = *Credit card*
* `` 'D' `` = *Pinless debit*
* `` 'K' `` = *Telecheck*
* `` 'P' `` = *PayPal*


__Types of Transactions possible (TRANSACTION\_TYPES)___

* `` 'S' `` = *Sale transaction*
* `` 'C' `` = *Credit*
* `` 'A' `` = *Authorization*
* `` 'D' `` = *Delayed Capture*
* `` 'V' `` = *Void*
* `` 'F' `` = *Voice Authorization*
* `` 'I' `` = *Inquiry*
* `` 'N' `` = *Duplicate transaction*
* `` 'R' `` = *Recurring*


## Requirements

* Python 2.5+

The recurring payment functionality of this library requires the PayflowPro 
account to have the Recurring Billing module activated (additional costs apply).
Likewise with the Security Code & Address Verification module.


## Usage

Refer to the ``client.py`` file in the ``tests`` subdirectory for example usage of the client.

To run the tests you will have to edit the file and set the following variables with a valid Payflow Pro Account.

* ``PARTNER_ID``
* ``VENDOR_ID``
* ``USERNAME``
* ``PASSWORD``
