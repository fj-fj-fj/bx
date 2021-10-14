#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

# https://github.com/leshchenko1979/fast_bitrix24
from fast_bitrix24 import Bitrix  # type: ignore

if os.getenv('BITRIX_EMULATION'):
    from emulation.client import Bitrix  # noqa: F811

# CBR
CBR_URL = os.getenv('CBR_URL', 'https://www.cbr-xml-daily.ru/daily_json.js')

# Bitrix
COMPANY = os.getenv('COMPANY')
USER_ID = os.getenv('USER_ID')
SECRET_TOKEN = os.getenv('SECRET_TOKEN')
BX_URL = f'https://{COMPANY}.bitrix24.ru/rest/{USER_ID}/{SECRET_TOKEN}'


# Я допускаю, что идентификаторы валют в битриксе такие:
def get_bx_valutes() -> dict[str, int]:
    return dict(EUR=1, USD=2, KZT=3, PLN=4)


def get_webhook(bx_url: str) -> Bitrix:
    return Bitrix(bx_url)
