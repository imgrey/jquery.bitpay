"""
Celery asynchronous task, that queries bitpay.com API server.
"""
from django.utils import simplejson
from celery.task import Task, periodic_task
from django.conf import settings

import logging

if settings.DEBUG:
    logging.basicConfig(level=logging.DEBUG)

class BitPayInvoice(Task):
    """
    Send request for invoice creation
    """

    def curl(self, url, api_key, post=False):
        import urllib2
        import urllib
        import base64

        response = ""
        if url.strip() != '' and api_key.strip() != '':

            cookie_handler=urllib2.HTTPCookieProcessor()
            redirect_handler=urllib2.HTTPRedirectHandler()
            opener = urllib2.build_opener(redirect_handler, cookie_handler)

            uname = base64.b64encode(api_key)

            opener.addheaders = [
                ('Content-Type', 'application/json'),
                ('Authorization', 'Basic ' + uname),
                ('X-BitPay-Plugin-Info', 'pythonlib1.1'),
            ]

            if post:
                responseString = opener.open(url, urllib.urlencode(
                    simplejson.loads(post))).read()
            else:
                responseString = opener.open(url).read()

            try:
                response = simplejson.loads(responseString)
            except ValueError:
                response = {
                    "error": responseString
                }
        return response

    def create_invoice(self, orderId, price, desc, buyer_email, cart_id):
        """
        @return array response
        """
        from django.core.urlresolvers import reverse

        site_domain = getattr(settings, 'SITE_DOMAIN', '')
        api_key = getattr(settings, 'BITPAY_API_SECRET_KEY', '')
        options = dict([
            ('notificationEmail', getattr(settings, 'BITPAY_NOTIFICATION_EMAIL', '')),
            ('notificationURL', getattr(settings, 'BITPAY_NOTIFICATION_URL', '')),
            ('redirectURL', "http://%s%s"%(site_domain, reverse('bitpay_succes'))),
            ('currency', 'USD'),
            ('physical', 'true'),
            ('fullNotifications', 'true'),
            ('transactionSpeed', 'low'),
            ('itemDesc', desc),
            ('buyerEmail', buyer_email),
        ])

        posData = cart_id
        pos = {
            'posData': posData,
        }

        if getattr(settings, 'BITPAY_VERIFY_POST'):
            pos['hash'] = self.bp_hash(str(posData), api_key)

        options['posData'] = simplejson.dumps(pos)

        if len(options['posData']) > 100:
            return {
                "error": "posData > 100 character limit. Are you using the posData hash?"
            }

        options['orderID'] = orderId
        options['price'] = price

        postOptions = ['orderID', 'itemDesc', 'itemCode', 'notificationEmail',
            'notificationURL', 'redirectURL', 'posData', 'price', 'currency',
            'physical', 'fullNotifications', 'transactionSpeed', 'buyerName',
            'buyerAddress1', 'buyerAddress2', 'buyerCity', 'buyerState',
            'buyerZip', 'buyerEmail', 'buyerPhone']

        """
        postOptions = ['orderID', 'itemDesc', 'itemCode', 'notificationEmail',
            'notificationURL', 'redirectURL', 'posData', 'price', 'currency',
            'physical', 'fullNotifications', 'transactionSpeed', 'buyerName',
            'buyerAddress1', 'buyerAddress2', 'buyerCity', 'buyerState',
            'buyerZip', 'buyerEmail', 'buyerPhone', 'pluginName',
            'pluginVersion', 'serverInfo', 'serverVersion', 'addPluginInfo'];
        """

        for o in postOptions:
            if o in options:
                pos[o] = options[o]

        pos = simplejson.dumps(pos)

        response = self.curl('https://bitpay.com/api/invoice/', api_key, pos)

        logging.debug("Create Invoice: ")
        logging.debug(pos)
        logging.debug("Response: ")
        logging.debug(response)

        return response

    def bp_hash(self, data, key):
        """
        Generates a base64 encoded keyed hash.
        """
        from hashlib import sha256
        import hmac
        import binascii

        hashed = hmac.new(key, data, sha256)
        return binascii.b2a_base64(hashed.digest())[:-1]

    def verify_notification(self, data):

        jsondata = simplejson.loads(data)
        if 'posData' not in jsondata:
            return None

        api_key = getattr(settings, 'BITPAY_API_SECRET_KEY', '')

        posData = simplejson.loads(jsondata['posData'])
        if getattr(settings, 'BITPAY_VERIFY_POST') \
            and posData['hash'] != self.bp_hash(str(posData['posData']),
                api_key):
            return False
        return jsondata

    def get_invoice(self, invoice_id):
        """
        Retrieves an invoice from BitPay.
        """

        api_key = getattr(settings, 'BITPAY_SECRET_API_KEY', '')
        response = self.curl('https://bitpay.com/api/invoice/%s'%invoice_id,
            api_key)
        print response
        response['posData'] = simplejson.loads(response['posData'])
        response['posData'] = response['posData']['posData']
        return response

    def run(self, order_id, price, desc, buyer_email, cart_id):
        """
        Returns URL of BitPay invoice or error.
        """
        return self.create_invoice(order_id, price, desc, buyer_email, cart_id)
