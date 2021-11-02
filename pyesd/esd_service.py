import requests
from datetime import datetime

class ESD:
    def __init__(self, username, password, endpoint, query_endpoint, vat_rate = 0.18) -> None:
        self.esd_username = username
        self.esd_password = password
        self.esd_endpoint = endpoint
        self.esd_query_endpoint = query_endpoint
        self.vat_rate = vat_rate

    def query(self, invoice_id: str) -> dict:
        try:
            return requests.get(
                url=f'{self.esd_query_endpoint}/{invoice_id}?username={self.esd_username}&password={self.esd_password}',
                json={
                    'invoice_number': invoice_id,
                    'username': self.esd_username,
                    'password': self.esd_password
                }
            ).json()
        except Exception as e:
            print(str(e))

    def post(self, invoice_id: str, amount: float) -> dict:
        net_amount = amount / (self.vat_rate + 1)
        try:
            date = datetime.now()
            return requests.post(
                url=self.esd_endpoint,
                json={
                    'invoice_date': f'{date.day}/{date.month}/{date.year}',
                    'invoice_number': invoice_id,
                    'vat_amount': net_amount * self.vat_rate,
                    'gross_amount': amount * (1 - self.vat_rate),
                    'invoice_total': amount,
                    'username': self.esd_username,
                    'password': self.esd_password
                }
            ).json()
        except Exception as e:
            print(str(e))
