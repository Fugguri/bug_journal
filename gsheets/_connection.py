# First, set up a callback function that fetches our credentials off the disk.
# gspread_asyncio needs this to re-authenticate when credentials expire.
from pathlib import Path

import gspread_asyncio
import pygsheets

from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def get_creds():
    # To obtain a service account JSON file, follow these steps:
    # https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account
    creds = Credentials.from_service_account_file("gis-gkh-dce0833e31ca.json")
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped


__agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)
__gc = pygsheets.authorize(service_file='./gis-gkh-dce0833e31ca.json')
# worksheet = __gc.open_by_url(
#     'https://docs.google.com/spreadsheets/d/1jNn7XyYLPu4p0B6-RaQdFkUgpGB7m-OICv__jK9N6eM/edit#gid=0')
worksheet = __gc.open_by_url(
    'https://docs.google.com/spreadsheets/d/1xJit_DqLW5tSZ61KO9hBCGXTYhgmhvsFWn86gSxITDU/edit#gid=1060314088')

auth = GoogleAuth()
scope = ["https://www.googleapis.com/auth/drive"]
auth.credentials = ServiceAccountCredentials.from_json_keyfile_name('./gis-gkh-dce0833e31ca.json', scope)
drive = GoogleDrive(auth)


async def get_sheet_by_title(title: str) -> gspread_asyncio.AsyncioGspreadWorksheet:
    agc = await __agcm.authorize()
    sh = await agc.open_by_url('https://docs.google.com/spreadsheets/d/1jNn7XyYLPu4p0B6-RaQdFkUgpGB7m-OICv__jK9N6eM/edit#gid=0')
    sheet = await sh.worksheet(title)
    return sheet


async def add_sheet(title: str) -> gspread_asyncio.AsyncioGspreadWorksheet:
    agc = await __agcm.authorize()
    sh = await agc.open_by_url(
        'https://docs.google.com/spreadsheets/d/1jNn7XyYLPu4p0B6-RaQdFkUgpGB7m-OICv__jK9N6eM/edit#gid=0'
    )
    sheet = await sh.add_worksheet(title, rows=500, cols=25)
    return sheet


async def delete_sheet(sheet: gspread_asyncio.AsyncioGspreadWorksheet) -> None:
    agc = await __agcm.authorize()
    sh = await agc.open_by_url(
        'https://docs.google.com/spreadsheets/d/1jNn7XyYLPu4p0B6-RaQdFkUgpGB7m-OICv__jK9N6eM/edit#gid=0')
    await sh.del_worksheet(sheet)
