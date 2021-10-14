#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import unittest
import re
from datetime import datetime

import requests

# Unittest tests order.
# https://stackoverflow.com/questions/4095319/unittest-tests-order#comment120033036_22317851
unittest.TestLoader.sortTestMethodsUsing = lambda *args: -1


def get_now_timestamp():
    """UTC to ISO 8601 with Local TimeZone information without microsecond."""
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def replace_minutes_and_seconds(timestamp: str) -> str:
    """
    >>> replace_minutes('2021-10-14T16:14:29+03:00')
    '2021-10-14T16****+03:00'
    """
    return timestamp.replace(re.findall(':\d*:\d*\+', timestamp)[0], '****+')  # noqa: W605 E501


def configure_logging(file: str = 'interaction.log', lvl: int = logging.INFO):
    logger = logging.getLogger(name='root')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(file)
    fh.setLevel(lvl)
    logger.addHandler(fh)


class FunctionalTest(unittest.TestCase):

    def setUp(self):
        self.url = 'http://127.0.0.1:5000/'
        self.assertEqual.__self__.maxDiff = None

    def test_create_new_client_with_new_deal(self):
        """
        Client "Jon" doesn't exist.
        Creation of "Jon" and his deal.
        Creation of "Contact-Deal" relationship.
        """

        with open('emulation/crm/contacts/list.json') as f_contacts, \
            open('emulation/crm/deal/list.json') as f_deal:  # noqa: E125
            contacts_list_empty = json.loads(f_contacts.read())
            deal_list_empty = json.loads(f_deal.read())
        self.assertEqual(contacts_list_empty, {"contacts": []})
        self.assertEqual(deal_list_empty, {"deal": []})

        post_data = {
            "title": "title",
            "description": "Some description",
            "client": {
                "name": "Jon",
                "surname": "Karter",
                "phone": "+77777777777",
                "adress": "st. Mira, 287, Moscow"
            },
            "products": ["Candy", "Carrot", "Potato"],
            "delivery_adress": "st. Mira, 211, Ekaterinburg",
            "delivery_date": "2021-01-01:16:00",
            "delivery_code": "#232nkF3fAdn"
        }
        requests.post(self.url, json=post_data)

        with open('emulation/crm/contacts/list.json') as f:
            contacts_list_with_client_jon = f.read()

        expected_contacts_list = json.dumps({
            "contacts": [
                {
                    "id": 1,
                    **post_data['client'],
                    "deal": [
                        "#232nkF3fAdn"
                    ]
                }
            ]
        })
        self.assertEqual(contacts_list_with_client_jon, expected_contacts_list)

        with open('emulation/crm/deal/list.json') as f:
            deal_list_with_client_jon = f.read()

        expected_deal_list = json.dumps({
            "deal": [
                {
                    "id": 1,
                    **post_data
                }
            ]
        })
        self.assertEqual(deal_list_with_client_jon, expected_deal_list)

    def test_no_action_because_client_and_deal_exist(self):
        """
        The client "Jon" and his deal exist.
        None action.
        """

        with open('emulation/crm/contacts/list.json') as f_contacts, \
            open('emulation/crm/deal/list.json') as f_deal:  # noqa: E125
            client_jon_exists = f_contacts.read()
            deal_with_client_jon_exists = f_deal.read()

        post_data = {
            "title": "title",
            "description": "Some description",
            "client": {
                "name": "Jon",
                "surname": "Karter",
                "phone": "+77777777777",
                "adress": "st. Mira, 287, Moscow"
            },
            "products": ["Candy", "Carrot", "Potato"],
            "delivery_adress": "st. Mira, 211, Ekaterinburg",
            "delivery_date": "2021-01-01:16:00",
            "delivery_code": "#232nkF3fAdn"
        }

        expected_contacts_list = json.dumps({
            "contacts": [
                {
                    "id": 1,
                    **post_data['client'],
                    "deal": [
                        "#232nkF3fAdn"
                    ]
                }
            ]
        })
        self.assertEqual(client_jon_exists, expected_contacts_list)

        expected_deal_list = json.dumps({
            "deal": [
                {
                    "id": 1,
                    **post_data
                }
            ]
        })
        self.assertEqual(deal_with_client_jon_exists, expected_deal_list)

        requests.post(self.url, json=post_data)

        with open('emulation/crm/contacts/list.json') as f:
            contacts_list_with_client_jon = f.read()
        self.assertEqual(contacts_list_with_client_jon, expected_contacts_list)

        with open('emulation/crm/deal/list.json') as f:
            deal_list_with_client_jon = f.read()
        self.assertEqual(deal_list_with_client_jon, expected_deal_list)

    def test_update_deal(self):
        """
        The client "Jon" and his deal exist, but .
        But there are differences in the new deal.
        Old deal will be updated.
        """

        with open('emulation/crm/contacts/list.json') as f_contacts, \
            open('emulation/crm/deal/list.json') as f_deal:  # noqa: E125
            client_jon_exists = f_contacts.read()
            deal_with_client_jon_exists = f_deal.read()

        old_deal = {
            "title": "title",
            "description": "Some description",
            "client": {
                "name": "Jon",
                "surname": "Karter",
                "phone": "+77777777777",
                "adress": "st. Mira, 287, Moscow"
            },
            "products": ["Candy", "Carrot", "Potato"],
            "delivery_adress": "st. Mira, 211, Ekaterinburg",
            "delivery_date": "2021-01-01:16:00",
            "delivery_code": "#232nkF3fAdn"
        }

        expected_contacts_list = json.dumps({
            "contacts": [
                {
                    "id": 1,
                    **old_deal['client'],
                    "deal": [
                        "#232nkF3fAdn"
                    ]
                }
            ]
        })
        self.assertEqual(client_jon_exists, expected_contacts_list)

        expected_deal_list = json.dumps({
            "deal": [
                {
                    "id": 1,
                    **old_deal
                }
            ]
        })
        self.assertEqual(deal_with_client_jon_exists, expected_deal_list)

        new_deal = {
            "title": "NEW TITLE",  # won't update
            "description": "NEW DESCRIPTION",  # won't update
            "client": {
                "name": "Jon",
                "surname": "Karter",
                "phone": "+77777777777",
                "adress": "st. Mira, 287, Moscow"
            },
            "products": ["Candy", "Carrot", "Potato", "Cheese"],  # nu
            "delivery_adress": "st. Mira, 221, Ekaterinburg",  # nu
            "delivery_date": "2021-01-01:20:00",  # nu
            "delivery_code": "#232nkF3fAdn"
        }

        requests.post(self.url, json=new_deal)

        expected_updated_deal_list = json.dumps({
            "deal": [
                {
                    "id": 1,
                    "title": "title",  # won't update
                    "description": "Some description",  # won't update
                    "client": {
                        "name": "Jon",
                        "surname": "Karter",
                        "phone": "+77777777777",
                        "adress": "st. Mira, 287, Moscow"
                    },
                    "products": ["Candy", "Carrot", "Potato", "Cheese"],  # nu
                    "delivery_adress": "st. Mira, 221, Ekaterinburg",  # nu
                    "delivery_date": "2021-01-01:20:00",  # nu
                    "delivery_code": "#232nkF3fAdn"
                }
            ]
        })

        with open('emulation/crm/deal/list.json') as f:
            deal_updated_success = f.read()
        self.assertEqual(deal_updated_success, expected_updated_deal_list)

    def test_create_second_client_with_deal(self):
        """
        Client "fj" doesn't exist.
        Creation of "fj" and his deal.
        Creation of "Contact-Deal" relationship.
        crm.contact.list has "Jon" and "fj" clients.
        """

        with open('emulation/crm/contacts/list.json') as f_contacts, \
            open('emulation/crm/deal/list.json') as f_deal:  # noqa: E125
            one_client_jon = f_contacts.read()
            one_deal_jon = f_deal.read()

        expected_one_client_jon = json.dumps({
            "contacts": [
                {
                    "id": 1,
                    "name": "Jon",
                    "surname": "Karter",
                    "phone": "+77777777777",
                    "adress": "st. Mira, 287, Moscow",
                    "deal": [
                        "#232nkF3fAdn"
                    ]
                }
            ]
        })

        self.assertEqual(one_client_jon, expected_one_client_jon)

        expected_one_deal_jon = json.dumps({
            "deal": [
                {
                    "id": 1,
                    "title": "title",
                    "description": "Some description",
                    "client": {
                        "name": "Jon",
                        "surname": "Karter",
                        "phone": "+77777777777",
                        "adress": "st. Mira, 287, Moscow"
                    },
                    "products": ["Candy", "Carrot", "Potato", "Cheese"],
                    "delivery_adress": "st. Mira, 221, Ekaterinburg",
                    "delivery_date": "2021-01-01:20:00",
                    "delivery_code": "#232nkF3fAdn"
                }
            ]
        })
        self.assertEqual(one_deal_jon, expected_one_deal_jon)

        new_client_data = {
            "title": "title",
            "description": "Some description",
            "client": {
                "name": "fj",
                "surname": "fj",
                "phone": "+66677777777",
                "adress": "Forks"
            },
            "products": ["Wine", "Coffee", "Fresh Blood"],
            "delivery_adress": "st. Mira, 212, Ekaterinburg",
            "delivery_date": "2021-01-02:00:00",
            "delivery_code": "#232nkF3ffoo"
        }

        requests.post(self.url, json=new_client_data)

        with open('emulation/crm/contacts/list.json') as f:
            contact_list_two_clients = f.read()

        expected_two_clients = json.dumps({
            "contacts": [
                {
                    "id": 1,
                    "name": "Jon",
                    "surname": "Karter",
                    "phone": "+77777777777",
                    "adress": "st. Mira, 287, Moscow",
                    "deal": [
                        "#232nkF3fAdn"
                    ]
                },
                {
                    "id": 2,
                    "name": "fj",
                    "surname": "fj",
                    "phone": "+66677777777",
                    "adress": "Forks",
                    "deal": [
                        "#232nkF3ffoo"
                    ]
                }
            ]
        })
        self.assertEqual(contact_list_two_clients, expected_two_clients)

        with open('emulation/crm/deal/list.json') as f:
            two_deals = f.read()

        expected_two_deals = json.dumps({
            "deal": [
                {
                    "id": 1,
                    "title": "title",
                    "description": "Some description",
                    "client": {
                        "name": "Jon",
                        "surname": "Karter",
                        "phone": "+77777777777",
                        "adress": "st. Mira, 287, Moscow"
                    },
                    "products": ["Candy", "Carrot", "Potato", "Cheese"],
                    "delivery_adress": "st. Mira, 221, Ekaterinburg",
                    "delivery_date": "2021-01-01:20:00",
                    "delivery_code": "#232nkF3fAdn"
                },
                {
                    "id": 2,
                    "title": "title",
                    "description": "Some description",
                    "client": {
                        "name": "fj",
                        "surname": "fj",
                        "phone": "+66677777777",
                        "adress": "Forks"
                    },
                    "products": ["Wine", "Coffee", "Fresh Blood"],
                    "delivery_adress": "st. Mira, 212, Ekaterinburg",
                    "delivery_date": "2021-01-02:00:00",
                    "delivery_code": "#232nkF3ffoo"
                }
            ]
        })
        self.assertEqual(two_deals, expected_two_deals)

    def test_add_deal(self):
        """
        Clients "Jon" and "fj" are exist.
        Adding new deal with "Jon".
        crm.contacts.list: Jon has 2 deals, fj has 1 deal.
        crm.deal.list has 3 deals.
        """

        with open('emulation/crm/contacts/list.json') as f_contacts, \
            open('emulation/crm/deal/list.json') as f_deal:  # noqa: E125
            two_clients_with_one_deal = f_contacts.read()
            two_deals = f_deal.read()

        Jon, fj = eval(two_clients_with_one_deal)['contacts']
        count_deal_jon = len(Jon['deal'])
        count_deal_fj = len(fj['deal'])
        self.assertEqual(count_deal_jon, 1)
        self.assertEqual(count_deal_fj, 1)

        deal_jon, deal_fj = eval(two_deals)['deal']
        self.assertEqual(deal_jon['delivery_code'], '#232nkF3fAdn')
        self.assertEqual(deal_fj['delivery_code'], '#232nkF3ffoo')

        new_deal_from_jon = {
            "title": "title",
            "description": "Some description",
            "client": {
                "name": "Jon",
                "surname": "Karter",
                "phone": "+77777777777",
                "adress": "st. Mira, 287, Moscow"
            },
            "products": ["Milk"],
            "delivery_adress": "st. Mira, 211, Ekaterinburg",
            "delivery_date": "2021-01-01:16:00",
            "delivery_code": "#232nkF3fbar"
        }

        requests.post(self.url, json=new_deal_from_jon)

        with open('emulation/crm/contacts/list.json') as f_contacts, \
            open('emulation/crm/deal/list.json') as f_deal:  # noqa: E125
            two_clients_with_one_deal = f_contacts.read()
            two_deals = f_deal.read()

        Jon, fj = eval(two_clients_with_one_deal)['contacts']
        count_deal_jon = len(Jon['deal'])
        count_deal_fj = len(fj['deal'])
        self.assertEqual(count_deal_jon, 2)
        self.assertEqual(count_deal_fj, 1)

        deal_jon_1, deal_fj, deal_jon_2 = eval(two_deals)['deal']
        self.assertEqual(deal_jon_1['delivery_code'], '#232nkF3fAdn')
        self.assertEqual(deal_fj['delivery_code'], '#232nkF3ffoo')
        self.assertEqual(deal_jon_2['delivery_code'], '#232nkF3fbar')

    def test_update_currency(self):
        """
        "www.cbr-xml-daily.ru/daily_json.js GET" request.
        Updating all valutes in Bitrix.
        """
        from interaction import CRM
        from settings import BX_URL, get_webhook, get_bx_valutes

        # Add logs into interaction.log
        # because `CRM._update('currency)` will be called manually.
        configure_logging()

        crm = CRM(get_webhook(BX_URL), {})._update('currency')
        self.assertEqual(crm, True)

        with open('emulation/crm/currency/update.json') as file_clean_data, \
            open('data/daily.json') as file_row_data:  # noqa: E125
            clean_data = json.loads(file_clean_data.read())
            row_data = json.loads(file_row_data.read())

        cbr_timestamp = replace_minutes_and_seconds(row_data['Timestamp'])
        now_timestamp = replace_minutes_and_seconds(get_now_timestamp())
        # Sometimes there may be such a problem:
        # - 2021-10-14T22****+03:00
        # ?             ^
        # + 2021-10-14T23****+03:00
        # ?             ^
        # Just restart in a minute :)
        self.assertEqual(cbr_timestamp, now_timestamp)

        # 1
        bx_usd_id = get_bx_valutes()['USD']
        # {'id': <id>, 'fields': {'Valute': <value>}}
        bx_usd = [v for v in clean_data['valutes'] if v['id'] == bx_usd_id][0]
        # <value>
        bx_usd_value = bx_usd['fields']['Valute']
        # <value>
        cbr_usd_value = row_data['Valute']['USD']['Value']
        self.assertEqual(cbr_usd_value, bx_usd_value)


def suite():
    """Create a callable test-suite generation added in desired order."""
    suite = unittest.TestSuite()
    suite.addTest(FunctionalTest('test_create_new_client_with_new_deal'))
    suite.addTest(FunctionalTest('test_no_action_because_client_and_deal_exist'))  # noqa: E501
    suite.addTest(FunctionalTest('test_update_deal'))
    suite.addTest(FunctionalTest('test_create_second_client_with_deal'))
    suite.addTest(FunctionalTest('test_add_deal'))
    suite.addTest(FunctionalTest('test_update_currency'))
    return suite


if __name__ == '__main__':
    # `failfast` is equivalentl a command line option, -f, or --failfast,
    # to stop the test run on the first error or failure.
    runner = unittest.TextTestRunner(failfast=True)
    runner.run(suite())
