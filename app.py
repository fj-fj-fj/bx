#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fast_bitrix24 import Bitrix
from flask import Flask, request

from settings import BX_URL, get_webhook
from interaction import CRM

app: Flask = Flask(__name__)

Webhook: Bitrix = get_webhook(BX_URL)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        deal: dict = request.json
        crm = CRM(Webhook, deal)
        responce = crm.create_or_update()
        return responce if isinstance(responce, dict) else 'OK'
    return 'OK'


if __name__ == '__main__':
    app.run()
