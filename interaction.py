#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import os
import requests
from copy import deepcopy
from typing import Any, Optional, Union

from fast_bitrix24 import Bitrix as true_bx

from emulation.client import Bitrix as false_bx
from settings import CBR_URL, get_bx_valutes, EXPECTED_JSON_KEYS


logging.basicConfig(level=logging.INFO)


class CRM:

    UPDATEBLE: tuple[str, str, str] = (
        'products',
        'delivery_adress',
        'delivery_date',
    )

    CATCHING_INTERNAL_ERRORS: tuple = (
        KeyError,
        TypeError,
    )

    def __init__(self, webhook: Union[true_bx, false_bx], deal: dict):
        logging.info('CRM INSTANCE CREATING ...')
        self._current_deal = deal
        self._webhook = webhook
        # will be setted in self._validate()
        self._validated_success: bool = False
        self._internal_errors: Optional[dict] = None
        # will be setted in self._api()
        self._bx_errors: Optional[dict] = None
        self._bx_responce: dict = {}
        # will be setted in self._client_exists()
        self._client_name: Optional[str] = None
        self._current_client: dict = {}
        # will be setted in self._deal_exists()
        self._delivery_code: Optional[str] = None
        self._fined_deal: dict = {}
        # will be setted in self._bind_client_with_deal()
        self._client_with_deal: dict = {}
        # will be setted in self._request()
        self._responce: dict = {}
        self._errors: Optional[dict] = None

    @staticmethod
    def _generate(error: tuple) -> dict[str, str]:
        return {"Error": (type(error).__name__), "Error description": str(error)}

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._webhook!r}, {self._current_deal!r})'

    def __str__(self) -> str:
        if self._validated_success:
            deal = (
                f"{{deal: ... '{self._current_deal['client']['name']}', "
                f"'{self._current_deal['client']['phone']}', "
                f"'{self._current_deal['delivery_code']}' }}"
            )
            # CRM(webhook, "{deal: ... 'name', 'phone', 'delivery_code' }")
            return f'{type(self).__name__}({self._webhook!r}, {deal!r})'
        return f'{type(self).__name__}({self._webhook!r}, no-validated-deal)>'

    def _validate(self, step: int = 0) -> bool:
        logging.info(f'\tself._validate({step=}) running ...')
        for key in EXPECTED_JSON_KEYS[step]:
            try:
                self._current_deal['client'][key] if step else self._current_deal[key]
            except self.CATCHING_INTERNAL_ERRORS as error:
                self._internal_errors = self._generate(error)
                self._validated_success = self._internal_errors is None
                logging.error(f'\tself._validate({step=}) raises {error!r}')
                logging.info(f'\tself._validate({step=}) {self._validated_success=}')
                return self._validated_success
        else:
            if step:
                self._validated_success = self._internal_errors is None
                logging.info(f'\tself._validate({step=}) {self._validated_success=}')
                return self._validated_success
            return self._validate(step=1)

    def _clent_exists(self, action: str = 'crm.contact.list') -> bool:
        logging.info(f'self._client_exists({action=}) running ...')

        if not self._validate():
            return False

        self._client_name = self._current_deal.get('client', {})['name']
        self._api(action)

        for contact in self._bx_responce.get('contacts', {}):
            if contact.get('name') == self._client_name:
                self._current_client = contact
                logging.info(f'self._client_exists(True): {self._current_client}\n')
                return True
        logging.info('self._client_exists(False)\n')
        return False

    def _deal_exists(self, action: str = 'crm.deal.list') -> bool:
        logging.info(f'self._deal_exists({action=}) running ...')

        self._delivery_code = self._current_deal.get('delivery_code')
        self._api(action)

        for deal in self._bx_responce.get('deal', {}):
            if deal.get('delivery_code') == self._delivery_code:
                self._fined_deal = deal
                logging.info(f'self._deal_exists(True) {self._fined_deal}\n')
                return True
        logging.info(f'self._deal_exists(False) {self._fined_deal}\n')
        return False

    def _api(self, operation: str, params: Optional[str] = None):
        logging.info(f'\tself._api({operation=}, {params=})')

        self._bx_responce = json.loads(
            self._webhook.get_all(operation, params=params),
        )
        logging.info(f'\tself._api() {self._bx_responce=}')
        assert isinstance(self._bx_responce, dict)

        self._bx_errors = self._check_errors('_bx_responce') and self._bx_responce or None
        if self._bx_errors:
            logging.error(f'CRM._api() sets {self._bx_errors=}')
            raise self._bx_errors['error_description']

    def _check_errors(self, responce: str) -> bool:
        return (res := getattr(self, responce)) and 'error' in res.keys()

    def _bind_client_with_deal(self, client_exist: bool = False):
        logging.info(f'\tself._bind_client_with_deal({client_exist=}) running ...')

        if client_exist:
            self._current_client['deal'].append(self._current_deal['delivery_code'])
        else:
            self._client_with_deal = deepcopy(dict(self._current_deal.get('client', {})))
            self._client_with_deal['deal'] = self._client_with_deal.get('deal', [])
            self._client_with_deal['deal'].append(self._current_deal['delivery_code'])

    def _equiualent(self) -> bool:
        return all([self._fined_deal[k] == self._current_deal[k] for k in self.UPDATEBLE])

    def _request(self, url: str = CBR_URL, format: str = 'json', save: bool = True):
        logging.info(f'self._request({url=}) running ...\n')

        result = getattr(requests.get(url), format)
        self._response = callable(result) and result() or result
        self._errors = self._check_errors('_responce') and self._responce or None

        if save and self._errors is None:
            self._save(self._response, 'data', 'daily.json', 'w', format)

        return self._errors is None

    def _save(self, data: Any, dir: str, file: str, mode: str, format: str):
        logging.info('self._save() running ...\n')

        os.makedirs(dir, exist_ok=True)
        with open(os.path.join(dir, file), mode) as f:
            if format == 'json':
                data = json.dumps(data, indent=4, ensure_ascii=False)
            f.write(data)

    def _update_currency(self):
        logging.info('\tself._update_currency() running ...\n')
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
        logging.info('\tself._update_fields() running ...')

        for key in self.UPDATEBLE:
            self._fined_deal.update({key: self._current_deal.get(key)})
        self._api('crm.deal.update', params=str(self._fined_deal))

        logging.info(f'self._update_fields() {self._bx_errors}')
        return self._bx_errors is not None

    def _update(self, entity: str = 'None') -> bool:
        logging.info(f'self._update() Updating {entity=} ...')

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
        logging.info(f'self._create() Creating new {entity=} ...')

        if self._internal_errors is not None:
            logging.info(f'self._create() {self._internal_errors=}')
            return False

        if entity == 'client':
            self._bind_client_with_deal()
            params = str(self._client_with_deal)
            self._api('crm.contact.add', params=params)
        elif entity == 'deal':
            self._update('client')
        params = str(self._current_deal)
        self._api('crm.deal.add', params=params)

        logging.info(f'self._create() {self._bx_errors=}\n')
        return self._bx_errors is None

    def create_or_update(self) -> Optional[Union[bool, dict]]:
        return self._clent_exists() and self._update()\
            or self._create()\
            or self._internal_errors\
            or self._bx_errors
