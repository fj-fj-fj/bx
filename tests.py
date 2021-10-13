import json
import unittest

import requests

# Unittest tests order.
# https://stackoverflow.com/questions/4095319/unittest-tests-order#comment120033036_22317851
unittest.TestLoader.sortTestMethodsUsing = lambda *args: -1


class FuntionalTest(unittest.TestCase):

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
                    "deal": "#232nkF3fAdn"
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


def suite():
    """Create a callable test-suite generation added in desired order."""
    suite = unittest.TestSuite()
    suite.addTest(FuntionalTest('test_create_new_client_with_new_deal'))
    suite.addTest(FuntionalTest('test_no_action_because_client_and_deal_exist'))  # noqa: E501
    suite.addTest(FuntionalTest('test_update_deal'))
    return suite


if __name__ == '__main__':
    # `failfast` is equivalentl a command line option, -f, or --failfast,
    # to stop the test run on the first error or failure.
    runner = unittest.TextTestRunner(failfast=True)
    runner.run(suite())
