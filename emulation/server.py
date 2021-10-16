#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
from ast import literal_eval
from typing import Optional, Union

from spyne import Application, rpc, ServiceBase, String
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication


class LocalBitrix(ServiceBase):

    CRM_CONTACTS = 'emulation/crm/contacts/list.json'
    CRM_DEALS = 'emulation/crm/deal/list.json'
    VALUTES = 'emulation/crm/currency/update.json'

    @staticmethod
    def add(crm_list: dict, key: str, params: str) -> str:
        last_contact_id = len(crm_list[key])
        new = {"id": last_contact_id + 1, **literal_eval(params)}
        crm_list.get(key, []).append(new)
        return json.dumps(crm_list)

    @staticmethod
    def data(file: str, data: Optional[str], mode: str, method: str) -> Union[str, int]:
        with open(file, mode) as f:
            return getattr(f, method)(data)

    @rpc(String, _returns=String)
    def crm_contact_list(ctx, params: str) -> str:
        logging.info('Server: crm.contact.list running ...')
        contacts_list: Union[str, int] = LocalBitrix.data(
            LocalBitrix.CRM_CONTACTS,
            data=None,
            mode='r',
            method='read',
        )
        assert isinstance(contacts_list, str)

        logging.info(f'crm_contact_list({params=}) -> {contacts_list}\n')
        return contacts_list

    @rpc(String, _returns=String)
    def crm_contact_add(ctx, params: str) -> str:
        logging.info('Server: crm.contact.add running ...')

        contacts_list: Union[str, int] = LocalBitrix.data(
            LocalBitrix.CRM_CONTACTS,
            data=None,
            mode='r',
            method='read',
        )
        assert isinstance(contacts_list, str)
        contacts_list: dict = json.loads(contacts_list)

        contacts_list_updated: str = LocalBitrix.add(
            contacts_list,
            key='contacts',
            params=params
        )

        characters_number: Union[str, int] = LocalBitrix.data(
            LocalBitrix.CRM_CONTACTS,
            data=contacts_list_updated,
            mode='w',
            method='write',
        )
        assert isinstance(characters_number, int)

        logging.info(f'crm_contact_add({params=}) -> {contacts_list_updated}\n')
        return contacts_list_updated

    @rpc(String, _returns=String)
    def crm_deal_list(ctx, params: str) -> str:
        logging.info('Server: crm.deal.list running ...')

        deal_list: Union[str, int] = LocalBitrix.data(
            LocalBitrix.CRM_DEALS,
            data=None,
            mode='r',
            method='read',
        )
        assert isinstance(deal_list, str)

        logging.info(f'crm_deal_list({params=}) -> {deal_list}\n')
        return deal_list

    @rpc(String, _returns=String)
    def crm_deal_add(ctx, params: str) -> str:
        logging.info('Server: crm.deal.add running ...')

        deal_list: Union[str, int] = LocalBitrix.data(
            LocalBitrix.CRM_DEALS,
            data=None,
            mode='r',
            method='read',
        )
        assert isinstance(deal_list, str)
        deal_list: dict = json.loads(deal_list)

        deal_list_updated: str = LocalBitrix.add(
            deal_list,
            key='deal',
            params=params,
        )

        characters_number: Union[str, int] = LocalBitrix.data(
            LocalBitrix.CRM_DEALS,
            data=deal_list_updated,
            mode='w',
            method='write',
        )
        assert isinstance(characters_number, int)

        logging.info(f'crm_deal_add({params=}) -> {deal_list_updated}\n')
        return deal_list_updated

    @rpc(String, _returns=String)
    def crm_deal_update(ctx, params: str) -> str:
        logging.info('Server: crm.deal.update running ...')

        deal_list: Union[str, int] = LocalBitrix.data(
            LocalBitrix.CRM_DEALS,
            data=None,
            mode='r',
            method='read',
        )
        assert isinstance(deal_list, str)
        deal_list: dict = json.loads(deal_list)

        updated_deal = literal_eval(params)
        for index, deal in enumerate(deal_list['deal']):
            if deal.get('delivery_code') == updated_deal['delivery_code']:
                deal_list.get('deal', [])[index] = updated_deal

        characters_number: Union[str, int] = LocalBitrix.data(
            LocalBitrix.CRM_DEALS,
            data=json.dumps(deal_list),
            mode='w',
            method='write',
        )
        assert isinstance(characters_number, int)

        logging.info(f'crm_deal_update({params=}) -> {deal_list}\n')
        return json.dumps(deal_list)

    @rpc(String, _returns=String)
    def crm_contact_update(ctx, params: str) -> str:
        logging.info('Server: crm.contact.update running ...')

        contacts_list: Union[str, int] = LocalBitrix.data(
            LocalBitrix.CRM_CONTACTS,
            data=None,
            mode='r',
            method='read',
        )
        assert isinstance(contacts_list, str)
        contacts_list: dict = json.loads(contacts_list)

        updated_contact = literal_eval(params)
        for contact in contacts_list['contacts']:
            if contact['name'] == updated_contact['name']:
                contact.update(updated_contact)

        characters_number: Union[str, int] = LocalBitrix.data(
            LocalBitrix.CRM_CONTACTS,
            data=json.dumps(contacts_list),
            mode='w',
            method='write',
        )
        assert isinstance(characters_number, int)

        logging.info(f'crm_contact_update({params=}) -> {contacts_list}\n')
        return json.dumps(contacts_list)

    @rpc(String, _returns=String)
    def crm_currency_update(ctx, params: str) -> str:
        logging.info('Server: rate running ...')

        characters_number: Union[str, int] = LocalBitrix.data(
            LocalBitrix.VALUTES,
            data=params,
            mode='w',
            method='write',
        )
        assert isinstance(characters_number, int)

        logging.info(f'rate({params=}) -> {params=}\n')
        return params


app = Application(
    [LocalBitrix],
    'api.emulation.server',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)


application = WsgiApplication(app)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    logging.basicConfig(level=logging.INFO)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)
    logging.info('listening to http://127.0.0.1:8000')
    logging.info('wsdl is at: http://localhost:8000/?wsdl\n')

    server = make_server('127.0.0.1', 8000, application)
    server.serve_forever()
