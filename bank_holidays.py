import requests
import json


def get_bank_holidays():
    response = requests.get('https://www.gov.uk/bank-holidays.json')
    data = json.loads(response.text)
    return data


def get_bank_holidays_for_year(region):
    holidays = []
    for key, value in get_bank_holidays().items():
        if key == region:
            for item in value['events']:
                holidays.append(item['date'])
            return holidays
    return None
