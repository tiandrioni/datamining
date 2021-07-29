"""
NeoWs (Near Earth Object Web Service) — веб-сервис RESTful для получения информации об астероидах, сближаемых с Землей.
С помощью NeoWs пользователь может: искать астероиды на основе их даты наибольшего сближения с Землей,
искать конкретный астероид с его идентификатором небольшого тела NASA JPL, а также просматривать общий набор данных.
"""

import requests
from pathlib import Path
from fake_headers import Headers
import json


params = {'api_key': 'DEMO_KEY',       # пользовался своим ключем
          'start_date': '2021-07-14',  # Starting date for asteroid search
          'end_date': '2021-07-15'}    # Ending date for asteroid search

url = 'https://api.nasa.gov/neo/rest/v1/feed'

headers = Headers(headers=True).generate()
req = requests.get(url, headers=headers, params=params)

file = Path(__file__).parent.joinpath('info.json')
file.write_text(json.dumps(req.json()))
