import json
import logging
import os
import requests
from copy import deepcopy
from typing import Any, Optional, Union

from fast_bitrix24 import Bitrix as true_bx  # type: ignore

from emulation.client import Bitrix as false_bx
from settings import CBR_URL, get_bx_valutes


logging.basicConfig(level=logging.INFO)


class CRM:

    UPDATEBLE: tuple[str, str, str] = (
        'products',
        'delivery_adress',
        'delivery_date',
    )

    def __init__(self, webhook: Union[true_bx, false_bx], deal: dict):
        logging.info('CRM INSTANCE CREATING ...')
        self._current_deal = deal
        self._webhook = webhook
        # will be setted in self._api()
        self._bx_errors: Optional[dict] = None
        self._bx_responce: Optional[dict] = None
        # will be setted in self._client_exists()
        self._client_name: Optional[str] = None
        self._current_client: Optional[dict] = None
        # will be setted in self._deal_exists()
        self._delivery_code: Optional[str] = None
        self._fined_deal: Optional[dict] = None
        # will be setted in self._bind_client_with_deal()
        self._client_with_deal: Optional[dict] = None
        # will be setted in self._request()
        self._responce: Optional[dict] = None
        self._errors: Optional[dict] = None

    def _clent_exists(self, action: str = 'crm.contact.list') -> bool:
        logging.info(f'self._client_exists({action=}): running ...\n')

        self._client_name = self._current_deal.get('client', {}).get('name')
        self._api(action)

        for contact in self._bx_responce.get('contacts'):  # type: ignore
            if contact.get('name') == self._client_name:
                self._current_client = contact
                return True
        return False

    def _deal_exists(self, action: str = 'crm.deal.list') -> bool:
        logging.info(f'self._deal_exists({action=}): running ...\n')

        self._delivery_code = self._current_deal.get('delivery_code')
        self._api(action)

        for deal in self._bx_responce.get('deal'):  # type: ignore
            if deal.get('delivery_code') == self._delivery_code:
                self._fined_deal = deal
                return True
        return False

    def _api(self, operation: str, params: Optional[str] = None):
        logging.info(f'self._api({operation=}): running ...\n{params=}\n')

        self._bx_responce = json.loads(
            self._webhook.get_all(operation, params=params),  # type: ignore
        )
        logging.info(f'CRM._api() sets {self._bx_responce=}\n')
        assert isinstance(self._bx_responce, dict)

        self._bx_errors = self._check_errors('_bx_responce') and self._bx_responce or None  # noqa: E501
        if self._bx_errors:
            logging.error(f'CRM._api() sets {self._bx_errors=}\n')
            raise self._bx_errors['error_description']

    def _check_errors(self, responce: str) -> bool:
        return (res := getattr(self, responce)) and 'error' in res.keys()  # type: ignore # noqa: E501

    def _bind_client_with_deal(self, client_exist: bool = False):
        logging.info(f'self._bind_client_with_deal({client_exist=}): running ...\n')  # noqa: E501

        if client_exist:
            self._current_client['deal'].append(self._current_deal['delivery_code'])  # type: ignore # noqa: E501
        else:
            self._client_with_deal = deepcopy(self._current_deal.get('client'))
            self._client_with_deal['deal'] = self._client_with_deal.get('deal', [])  # type: ignore # noqa: E501
            self._client_with_deal['deal'].append(self._current_deal['delivery_code'])  # type: ignore # noqa: E501

    def _equiualent(self) -> bool:
        return all(
            [self._fined_deal[k] == self._current_deal[k] for k in self.UPDATEBLE]  # type: ignore # noqa: E501
        )

    def _request(self, url: str = CBR_URL, format: str = 'json', save: bool = True):  # noqa: E501
        logging.info(f'self._request({url=}): running ...\n')

        result = getattr(requests.get(url), format)
        self._response = callable(result) and result() or result
        self._errors = self._check_errors('_responce') and self._responce or None  # noqa: E501

        if save and self._errors is None:
            self._save(self._response, 'data', 'daily.json', 'w', format)

        return self._errors is None

    def _save(self, data: Any, dir: str, file: str, mode: str, format: str):
        logging.info('self._save(): running ...\n')

        os.makedirs(dir, exist_ok=True)
        with open(os.path.join(dir, file), mode) as f:
            if format == 'json':
                data = json.dumps(data, indent=4, ensure_ascii=False)
            f.write(data)

    def _update_currency(self):
        logging.info('self._update_currency(): running ...\n')
        assert self._errors is None

        params = {'valutes': []}
        for valute, valute_id in get_bx_valutes().items():
            valute_value: float = self._response['Valute'][valute]['Value']
            params['valutes'].append({
                'id': valute_id,
                'fields': {
                    'Valute': valute_value
                }
            })
        params = json.dumps(params)
        self._api('crm.currency.update', params=params)
        return self._bx_errors is None

    def _update_fields(self) -> bool:
        logging.info('self._update_fields(): running ...\n')

        for key in self.UPDATEBLE:
            self._fined_deal.update(  # type: ignore
                {key: self._current_deal.get(key)},
            )
        self._api('crm.deal.update', params=str(self._fined_deal))

        logging.warning(self._bx_errors)
        return self._bx_errors is not None

    def _update(self, entity: str = 'None') -> bool:
        logging.info(f'self._update(): Updating {entity} ...\n')

        if entity == 'None':
            success_or_not = self._deal_exists() and self._update('deal')\
                or self._create('deal')
        elif entity == 'deal':
            (eq := self._equiualent()) or (up := self._update_fields())
            success_or_not = eq or not(eq ^ up)
        elif entity == 'client':
            self._bind_client_with_deal(client_exist=True)
            params = str(self._current_client)
            self._api('crm.contact.update', params=params)
            success_or_not = self._bx_errors is None
        elif entity == 'currency':
            success_or_not = self._request() and self._update_currency()

        return success_or_not

    def _create(self, entity: str = 'client') -> bool:
        logging.info(f'self._create(): Creating new {entity} ...\n')

        if entity == 'client':
            self._bind_client_with_deal()
            params = str(self._client_with_deal)
            self._api('crm.contact.add', params=params)
        elif entity == 'deal':
            self._update('client')
        params = str(self._current_deal)
        self._api('crm.deal.add', params=params)

        return self._bx_errors is None

    def create_or_update(self) -> Optional[Union[bool, dict]]:
        return self._clent_exists() and self._update()\
            or self._create() or self._bx_errors
