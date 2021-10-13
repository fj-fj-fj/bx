import json
import logging
from ast import literal_eval
from typing import Optional, Union

from spyne import Application, rpc, ServiceBase, String  # type: ignore
from spyne.protocol.soap import Soap11  # type: ignore
from spyne.server.wsgi import WsgiApplication  # type: ignore


class LocalBitrix(ServiceBase):

    CRM_CONTACTS = 'emulation/crm/contacts/list.json'
    CRM_DEALS = 'emulation/crm/deal/list.json'

    @staticmethod
    def add(crm_list: dict, key: str, params: str) -> str:
        last_contact_id = len(crm_list[key])
        new = {"id": last_contact_id + 1, **literal_eval(params)}
        crm_list.get(key, []).append(new)
        return json.dumps(crm_list)

    @staticmethod
    def data(file: str, data: Optional[str], mode: str, method: str) -> Union[str, int]:  # noqa: E501
        with open(file, mode) as f:
            return getattr(f, method)(data)

    @rpc(String, _returns=String)
    def crm_contact_list(ctx, params: str) -> str:
        logging.info('Server: crm.contact.list running ...')
        contacts_list: str = LocalBitrix.data(  # type: ignore
            LocalBitrix.CRM_CONTACTS,
            data=None,
            mode='r',
            method='read',
        )
        logging.info(f'crm_contact_list({params=}) -> {contacts_list}\n')
        return contacts_list

    @rpc(String, _returns=String)
    def crm_contact_add(ctx, params: str) -> str:
        logging.info('Server: crm.contact.add running ...')

        contacts_list: dict = json.loads(LocalBitrix.data(  # type: ignore
            LocalBitrix.CRM_CONTACTS,
            data=None,
            mode='r',
            method='read',
        ))

        contacts_list_updated: str = LocalBitrix.add(
            contacts_list,
            key='contacts',
            params=params
        )

        characters_number = LocalBitrix.data(
            LocalBitrix.CRM_CONTACTS,
            data=contacts_list_updated,
            mode='w',
            method='write',
        )
        assert isinstance(characters_number, int)

        logging.info(f'crm_contact_add({params=}) -> {contacts_list_updated}\n')  # noqa: E501
        return contacts_list_updated

    @rpc(String, _returns=String)
    def crm_deal_list(ctx, params: str) -> str:
        logging.info('Server: crm.deal.list running ...')

        deal_list: str = LocalBitrix.data(  # type: ignore
            LocalBitrix.CRM_DEALS,
            data=None,
            mode='r',
            method='read',
        )
        logging.info(f'crm_deal_list({params=}) -> {deal_list}\n')
        return deal_list

    @rpc(String, _returns=String)
    def crm_deal_add(ctx, params: str) -> str:
        logging.info('Server: crm.deal.add running ...')

        deal_list: dict = json.loads(LocalBitrix.data(  # type: ignore
            LocalBitrix.CRM_DEALS,
            data=None,
            mode='r',
            method='read',
        ))

        deal_list_updated: str = LocalBitrix.add(
            deal_list,
            key='deal',
            params=params,
        )

        characters_number = LocalBitrix.data(
            LocalBitrix.CRM_DEALS,
            data=deal_list_updated,
            mode='w',
            method='write',
        )
        assert isinstance(characters_number, int)

        logging.info(f'crm_deal_add({params=}) -> {deal_list_updated}\n')
        return deal_list_updated


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
