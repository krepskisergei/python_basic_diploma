import requests
import json

url = "https://hotels4.p.rapidapi.com/locations/search"
url = "https://hotels4.p.rapidapi.com/properties/list"
querystring = {
    'query': 'moscow',
    'locale': 'ru_RU'
}
querystring = {
    "destinationId":"1153093",
    "pageNumber":"1",
    "pageSize":"25",
    "checkIn":"2021-09-25",
    "checkOut":"2021-09-26",
    "adults1":"1",
    "sortOrder":"PRICE",
    "locale":"ru_RU",
    "currency":"RUR"
}
headers = {
    'x-rapidapi-host': 'hotels4.p.rapidapi.com',
    'x-rapidapi-key': '2573c95c2cmsh0501bf0ff0ee6bap10735fjsn1db6b0e05ce1'
}
response = requests.request('GET', url, headers=headers, params=querystring)
data = json.loads(response.text)
print(data)