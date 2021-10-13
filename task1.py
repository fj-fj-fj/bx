import os
import requests

from fast_bitrix24 import Bitrix  # type: ignore

from settings import BX_URL, CBR_URL, get_bx_valutes, get_webhook


VALUTES = get_bx_valutes()


def daily(cbr_url: str) -> dict:
    return requests.get(cbr_url).json()


def save(data: dict, dir: str = 'src/api/data', file: str = 'daily.json'):
    os.makedirs(dir, exist_ok=True)
    with open(os.path.join(dir, file), 'w') as f:
        f.write(__import__('json').dumps(data, indent=4, ensure_ascii=False))


def update_bx24(webhook: Bitrix, daily_data: dict):
    try:
        for valute, valute_id in VALUTES.items():
            valute_value: float = daily_data['Valute'][valute]['Value']
            _crm_currency_update(webhook, valute_id, valute_value)
    except KeyError:
        raise KeyError(daily)


def _crm_currency_update(webhook: Bitrix, valute_id: int, valute_value: float):
    # Метод `crm.currency.update` обновляет существующую валюту
    # - https://dev.1c-bitrix.ru/rest_help/crm/currency/crm_currency_update.php
    # У меня нет доступа обновлять где-нибудь курсы валют
    # поэтому допустим, что это сработает (то есть просто обновим каждую)
    webhook.get_all(
        'crm.currency.update',
        params={
            'id': valute_id,
            'fields': {'Value': valute_value},
        },
    )


def main(
    bx_url: str = BX_URL,
    cbr_url: str = CBR_URL,
    save_local: bool = True
):
    daily_data = daily(cbr_url)
    assert isinstance(daily_data, dict)

    webhook = get_webhook(bx_url)

    save_local and save(daily_data)

    update_bx24(webhook, daily_data)


if __name__ == '__main__':
    main()
