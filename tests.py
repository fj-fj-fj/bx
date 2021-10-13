import json
import unittest

import requests

# Unittest tests order.
# https://stackoverflow.com/questions/4095319/unittest-tests-order#comment120033036_22317851
unittest.TestLoader.sortTestMethodsUsing = lambda *args: -1


class Test(unittest.TestCase):

    def setUp(self):
        self.url = 'http://127.0.0.1:5000/'
        self.assertEqual.__self__.maxDiff = None

    def test_create_client_with_deal(self):
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
                    "deal": "#232nkF3fAdn"
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

    def test_client_and_deal_exist(self):
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
                    "deal": "#232nkF3fAdn"
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


if __name__ == '__main__':
    unittest.main()
