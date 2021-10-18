#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from typing import Optional

import requests
import zeep

URL = os.getenv('WSDL_URL', 'http://127.0.0.1:8000/?wsdl')


class Bitrix:

    def __init__(self, *args, **kwargs):
        try:
            self._client = zeep.Client(wsdl=URL)
        except requests.exceptions.ConnectionError as e:
            print(repr(e))
            os.system('make check_connections && code app.log')

    def get_all(self, operation: str, params: Optional[str]) -> str:
        operation = operation.replace('.', '_')

        for service in self._client.wsdl.services.values():
            if service.name == 'LocalBitrix':
                for port in service.ports.values():
                    for _operation in port.binding._operations.values():
                        if _operation.name == operation:
                            return getattr(self._client.service, operation)(params)

        return '{"error": "OperationError", "error_description": "Operation does not exist."}'


if __name__ == '__main__':
    try:
        for service in zeep.Client(wsdl=URL).wsdl.services.values():
            print('Service:', service.name)
            for port in service.ports.values():
                for operation in port.binding._operations.values():
                    print('Method:', operation.name)
                    print('    parameter:', operation.input.signature())
    except requests.exceptions.ConnectionError:
        os.system('make check_connections && code app.log')
