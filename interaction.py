import json
import logging
from copy import deepcopy
from typing import Iterable, Optional, Union

from fast_bitrix24 import Bitrix as true_bx  # type: ignore
from emulation.client import Bitrix as false_bx


logging.basicConfig(level=logging.INFO)


class CRM:

    def __init__(self, webhook: Union[true_bx, false_bx], deal: dict):
        logging.info('CRM instance creating with new deal ...')
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

    def _clent_exists(self, action: str = 'crm.contact.list') -> bool:
        self._client_name = self._current_deal.get('client', {}).get('name')
        self._api(action)

        for contact in self._bx_responce.get('contacts'):  # type: ignore
            if contact.get('name') == self._client_name:
                self._current_client = contact
                return True
        return False

    def _deal_exists(self, action: str = 'crm.deal.list') -> bool:
        self._delivery_code = self._current_deal.get('delivery_code')
        self._api(action)

        for deal in self._bx_responce.get('deal'):  # type: ignore
            if deal.get('delivery_code') == self._delivery_code:
                self._fined_deal = deal
                return True
        return False

    def _api(self, operation: str, params: Optional[str] = None):
        self._bx_responce = json.loads(
            self._webhook.get_all(operation, params=params),  # type: ignore
        )
        logging.info(f'CRM._api() sets {self._bx_responce=}\n')
        assert isinstance(self._bx_responce, dict)

        self._bx_errors = self._check_errors() and self._bx_responce or None
        if self._bx_errors:
            logging.error(f'CRM._api() sets {self._bx_errors=}\n')
            raise self._bx_errors['error_description']

    def _check_errors(self) -> bool:
        return self._bx_responce and 'error' in self._bx_responce.keys()  # type: ignore # noqa: E501

    def _bind_client_with_deal(self):
        self._client_with_deal = deepcopy(self._current_deal.get('client'))
        self._client_with_deal['deal'] = self._current_deal['delivery_code']

    def _equiualent(self, keys: Iterable) -> bool:
        return all([self._fined_deal[k] == self._current_deal[k] for k in keys])  # type: ignore # noqa: E501

    def _update_fields(self, keys: Iterable) -> bool:
        logging.info('self._update_fields(): running ...')
        for key in keys:
            self._fined_deal.update({key: self._current_deal.get(key)})  # type: ignore # noqa: E501
        self._api('crm.deal.update', params=str(self._fined_deal))
        logging.warning(self._bx_errors)
        return self._bx_errors is not None

    def _update(
        self,
        entity: str = 'client',
        keys: Iterable = ('products', 'delivery_adress', 'delivery_date'),
    ) -> bool:
        logging.info(f'self._update(): Updating {entity} ...')
        if entity == 'client':
            success_or_not = self._deal_exists() and self._update('deal') or self._create('deal')  # noqa: E501
        elif entity == 'deal':
            (eq := self._equiualent(keys)) or (up := self._update_fields(keys))
            success_or_not = eq or not(eq ^ up)
        return success_or_not

    def _create(self, entity: str = 'client') -> bool:
        logging.info(f'self._create(): Creating new {entity} ...')
        if entity == 'client':
            self._bind_client_with_deal()
            self._api('crm.contact.add', params=str(self._client_with_deal))  # noqa: E501
        self._api('crm.deal.add', params=str(self._current_deal))
        return self._bx_errors is None

    def create_or_update(self) -> Optional[Union[bool, dict]]:
        return self._clent_exists() and self._update() or self._create() or self._bx_errors  # noqa: E501
