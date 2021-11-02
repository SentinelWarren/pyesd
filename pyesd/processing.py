import json
import asyncio
import websockets

from datetime import datetime
from pyesd.esd_service import ESD

class SignPayments:	
    def __init__(self, db_uri, db_headers, esd_username, esd_password, endpoint, query_endpoint) -> None:
        self.uri = db_uri
        self.headers = db_headers
        self.esd = ESD(esd_username, esd_password, endpoint, query_endpoint)
        self.esd_success = 'Document signed successfully.'
    
    def _sign(self, entry: dict) -> dict:
        vat_entry_id = entry.get('id')
        vat_entry_type = entry.get('type')
        vat_entry_amount = entry.get('amount')
        internal_id = entry.get('internal_id')
        
        esd_check_reply = self.esd.query(vat_entry_id)
        signature = esd_check_reply.get('signature')
        description = esd_check_reply.get('description')
        
        if not signature:
            # This payment hasn't been signed yet so we sign it
            post_to_esd_result = self.esd.post(
                vat_entry_id,
                vat_entry_amount
            )
            signature = post_to_esd_result.get('signature')
            description = post_to_esd_result.get('description')
      
        if description == self.esd_success and signature:
            print(f'VAT submitted successfully for invoice <{vat_entry_id}>')
            # If successful, we can set it as handled
            return {
                'action': 'sign',
                'invoice_id': vat_entry_id,
                'internal_id': internal_id,
                'type': vat_entry_type,
                'signature': signature
            }
        else:
            print(f'Error submitting VAT for invoice <{vat_entry_id}>')
            return {
                'action': 'sign',
                'invoice_id': vat_entry_id,
                'internal_id': internal_id,
                'type': vat_entry_type,
                'signature': ''
            }

    def _sign_mock(self, entry: dict) -> dict:  # For testing only
        return {
            'action': 'sign',
            'invoice_id': entry.get('id'),
            'internal_id': entry.get('internal_id'),
            'type': entry.get('type'),
            'signature': 'izs341sdfze191vs7v2d1dfa'
        }

    async def run(self) -> None:
        async with websockets.connect(
            self.uri,
            extra_headers=self.headers
        ) as websocket:
            while True:
                try:
                    message = await websocket.recv()
                    payload = json.loads(message)
                    if payload.get('statusCode'):
                        print(f'\t\tResponse received from Tax Service: {message}')
                    else:
                        print(f'Request from Tax Service: {message}')
                        esd_response = json.dumps(
                            self._sign(  # TODO: Replace with _sign_mock(payload) when testing.
                                payload
                            )
                        )
                        await websocket.send(esd_response)
                        print(f'\tResponse sent from ESD: {esd_response}')
                except Exception as e:
                    print(f'Reconnecting: ({datetime.now()}) {str(e)}')
                    websocket = await websockets.connect(
                        self.uri,
                        extra_headers=self.headers
                    )


if __name__ == "__main__":
    # Adopt according to your valid working uri, api key & esd credentials.
    #
    # Company payments backend uri
    uri = 'wss://web.some_company.com/tax'
    headers = {
        'x-api-key': '3l4YgrBaUmh0nyIG0qT8jfkDRGbjdFG7lx'
    }

    # ESD invoice signing & querying ENDPOINT
    # Could be for example, a ngrok based https url instead of localhost 
    esd_endpoint = 'http://localhost:8084/esd/signinvoice'
    esd_query_endpoint = 'http://localhost:8084/esd/queryinvoice'

    # ESD Credentials
    esd_username = 'admin'
    esd_password = 'esdadmin2016'

    # Signing Invoices
    sign_invoices = SignPayments(uri, headers, esd_username, esd_password, esd_endpoint, esd_query_endpoint)
    asyncio.get_event_loop().run_until_complete(sign_invoices.run())
