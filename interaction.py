import json
import logging
from typing import Optional, Union

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

        for deal in self._current_deal.get('deal'):  # type: ignore
            if deal.get('delivery_code') == self._delivery_code:
                return True
        return False

    def _api(self, operation: str, params: Optional[str] = None):
        self._bx_responce = json.loads(
            self._webhook.get_all(operation, params=params),  # type: ignore
        )
        assert isinstance(self._bx_responce, dict)
        self._bx_errors = self._check_errors() and self._bx_responce or None
        logging.info(f'CRM._api() sets {self._bx_responce=}\n')
        if self._bx_errors:
            logging.error(f'CRM._api() sets {self._bx_errors=}\n')
            raise self._bx_errors['error_description']

    def _check_errors(self) -> bool:
        return self._bx_responce and 'error' in self._bx_responce.keys()  # type: ignore # noqa: E501

    def _create(self):
        logging.info('self._create(): Creating new client with deal ...')
        self._api('crm.contact.add', params=str(self._current_deal.get('client')))  # noqa: E501
        self._api('crm.deal.add', params=str(self._current_deal))

    def _update(self):
        logging.info('self._update(): Updating client or deal ...')
        self._api('crm.deal.update', params=str(self._current_deal))

    def create_or_update(self):
        self._clent_exists() and self._update() or self._create()
