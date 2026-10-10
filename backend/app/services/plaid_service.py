import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from dotenv import load_dotenv

load_dotenv()

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')

# Determine the Plaid Environment
if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox
elif PLAID_ENV == 'development':
    host = plaid.Environment.Development
elif PLAID_ENV == 'production':
    host = plaid.Environment.Production
else:
    host = plaid.Environment.Sandbox

# Configure Plaid Client
configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

def create_link_token(user_id: int):
    # Create a link_token for the given user
    request = LinkTokenCreateRequest(
        products=[Products("transactions")],
        client_name="FIN4YOU",
        country_codes=[CountryCode("US")],
        language='en',
        user=LinkTokenCreateRequestUser(
            client_user_id=str(user_id)
        )
    )
    response = client.link_token_create(request)
    return response['link_token']

def exchange_public_token(public_token: str):
    # Exchange public_token for access_token
    request = ItemPublicTokenExchangeRequest(
        public_token=public_token
    )
    response = client.item_public_token_exchange(request)
    return response['access_token'], response['item_id']

def sync_transactions(access_token: str, cursor: str = None):
    # Sync transactions for the given access token
    request = TransactionsSyncRequest(
        access_token=access_token,
        cursor=cursor
    )
    response = client.transactions_sync(request)
    return response['added'], response['modified'], response['removed'], response['next_cursor']
