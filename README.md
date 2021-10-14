# bx

## Bitrix24 interactions
Обновляет контакты, сделки и валюты, используя [Bitrix24 REST API](https://dev.1c-bitrix.ru/rest_help/index.php)  
(точнее не совсем)
#
> В общем у меня нет доступа к Битриксу, поэтому мой Битрикс  
это [emulation/server.py](emulation/server.py)  
А библиотекой  `fast-bitix24`, пусть служит [emulation/client.py](emulation/client.py)  
В [emulation/crm/](emulation/crm/) можно увидеть структуры, в которых сохраняются данные.

#
## Как работает
`CRM` объект получает на вход новую заявку.  
Проверяет, существует ли контакт, указанный в заявке.  
Если контакт не существует, создает его, заявку и связывает их.  
Если контакт есть, проверяет наличие такой же заявки по `delivery_code`.  
Если заявка есть и данные не отличаются, действий нет.  
Если заявка есть, но данные различны, обновляет данные.  
Если заявки нет, добавляет её к контакту.  
  
`CRM._update('currency')` обновляет курс валют, получая данные из ЦБ. (Это можно сделать пока только вручную.)  
Остальные действия автоматические, если стартовать [app.py](app.py) (и отправить json на http://127.0.0.1:5000/).  
   
Сама логика находится в [interaction.py](interaction.py).  
Посмтореть алгоритм можно в [interaction.log](interaction.log)  

#
## Использование

```bash
$ python3 -m venv .venv
$ . .venv/bin/activate

$ # Запустите soap сервер и приложение Flask:
$ make soap run
$ # Проверьте, работает ли все
$ # (port 5000: Flask, port 8000: Soap):
$ make check_connects
$ # Запустите тесты:
$ make test
$ # Для более подробной информации, прочтите Makefile.
$ # Отправьте данные через Postman или вручную*
```
`*` Структуру отправляемых данных можно посмотреть в [tests.py](tests.py) в `post_data`.  

#
## Установка
```bash
$ git clone https://github.com/fj-fj-fj/bx.git && cd bx
```

## Docker
```bash
$ docker build . --tag <image_name>
$ docker run --port 8001:8001 <image_name>
$ # Или используйте make цели (e.g., make up)
```