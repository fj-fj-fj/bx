# bx

## Bitrix24 interactions
Обновляет контакты, сделки и валюты, используя [Bitrix24 REST API](https://dev.1c-bitrix.ru/rest_help/index.php)  
(точнее не совсем)
#
> В общем у меня нет доступа к Битриксу, поэтому мой Битрикс  
это [emulation/server.py](emulation/server.py)  
А библиотекой, такой как  `fast-bitix24`, пусть служит [emulation/client.py](emulation/client.py)  
В [emulation/crm/](emulation/crm/) можно увидеть структуры, в которых сохраняются данные.

#
## Как работает
`CRM` объект ожидает на вход новую заявку.  
Проверяет, существует ли контакт, указанный пришедшей в заявке.  
Если контакт не существует, создает его, заявку и связывает их.  
Если контакт есть, проверяет наличие такой же заявки по `delivery_code`.  
Если заявка есть и данные не отличаются, действий нет.  
Если заявка есть, но данные различны, обновляет данные.  
Если заявки нет, добавляет её к контакту.  
  
`CRM._update('currency')` обновляет курс валют, получая данные из ЦБ (это можно сделать пока только вручную).  
Остальные действия автоматические, если стартовать [app.py](app.py) (и отправить json на http://127.0.0.1:5000/).  
   
Сама логика находится в [interaction.py](interaction.py).  
Посмотреть алгоритм можно в [interaction.log](interaction.log)  

#
## Зависимости
```bash
sudo apt-get update && sudo apt-get install direnv
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source .bashrc
# Или просто установите переменные из .envrc.sample
```

#
## Установка
```bash
git clone https://github.com/fj-fj-fj/bx.git && cd bx
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt
# Если direnv был установлен:
mv .envrc.sample .envrc
direnv allow
```

#
## Использование

```bash
# Запустите SOAP сервер и приложение Flask:
make soap run
# Проверьте, работает ли все
# (port 5000: Flask, port 8000: SOAP):
make check_connects
# Запустите тесты:
make test
# Для более подробнго управления, прочтите Makefile.
# Отправьте данные через Postman или вручную*
```
`*` Структуру отправляемых данных можно посмотреть в [tests.py](tests.py) в `post_data`.  

## Docker
```bash
sudo service docker start
docker build . --tag $(APP_NAME)
docker run --detach --tty --rm \
	--env WSDL_URL \
	--env BITRIX_EMULATION \
	--env CBR_URL \
	--env COMPANY \
	--env USER_ID \
	--env SECRET_TOKEN \
	--env FLASK_APP \
	--env FLASK_DEBUG \
	--env FLASK_ENV \
	--env TZ=$(cat /etc/timezone) \
	--name "$(APP_NAME)" $(APP_NAME)
# Или используйте make цели (e.g., make up)
```