from fastapi import FastAPI, HTTPException, Query
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = FastAPI()

# Путь к файлу credentials.json
credentials_path = './credentials.json'

# Указание необходимых разрешений для доступа к Google Spreadsheets
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# Создание клиента API Google Spreadsheets
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    credentials_path, scope)
client = gspread.authorize(credentials)

# Идентификатор таблицы Google Spreadsheets
spreadsheet_id = '1EIssM1H8lsTXTqHYV4_I_QhaFltrI6HJP3Owc86sxdk'


@app.get("/applications")
def get_applications(
    email: str = Query(None),
    telegram_id: str = Query(None),
    discord_id: str = Query(None)
):
    if not email and not telegram_id and not discord_id:
        raise HTTPException(
            status_code=400, detail="At least one parameter must be specified")

    params = [param for param in [
        email, telegram_id, discord_id] if param is not None]
    if len(params) > 1:
        raise HTTPException(
            status_code=400, detail="Only one parameter is allowed")

    try:
        # Открытие таблицы по идентификатору
        spreadsheet = client.open_by_key(spreadsheet_id)
        # Выбор листа, на котором находятся данные
        sheet = spreadsheet.sheet1

        # Фильтрация данных на основе запроса
        all_rows = sheet.get_all_records(
            empty2zero=False, head=1, default_blank="")
        filtered_rows = []
        for row in all_rows:
            if email and row.get("email") == email:
                filtered_rows.append(row)
            elif telegram_id and str(row.get("telegram_id")) == str(telegram_id):
                filtered_rows.append(row)
            elif discord_id and str(row.get("discord_id")) == str(discord_id):
                filtered_rows.append(row)

        # Добавление поля "id" к каждой записи
        applications = []
        for index, row in enumerate(filtered_rows):
            row["id"] = index + 1
            applications.append(row)

        return {"applications": applications}

    except gspread.exceptions.GSpreadException:
        raise HTTPException(
            status_code=500, detail="Failed to retrieve data from Google Spreadsheets")
