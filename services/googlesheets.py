import gspread
import logging
# TEST

gp = gspread.service_account(filename='services/kingdom.json')
gsheet = gp.open('G-money')
anketa = gsheet.worksheet("Анкета")


async def append_row(data: list) -> None:
    logging.info(f'append_row')
    anketa.append_row(data)
