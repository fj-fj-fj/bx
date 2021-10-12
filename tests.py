import json
import unittest

import requests


class Test(unittest.TestCase):

    def setUp(self):
        self.url = 'http://127.0.0.1:5000/'

    def test_create_client_with_deal(self):

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
                    **post_data['client']
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


if __name__ == '__main__':
    unittest.main()
