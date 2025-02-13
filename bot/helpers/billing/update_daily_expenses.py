from datetime import datetime

from bot.config import config
from bot.database.models.common import Currency
from bot.database.models.transaction import TransactionType, ServiceType
from bot.database.operations.transaction.getters import get_transactions_by_product_id_and_created_time
from bot.database.operations.transaction.writers import write_transaction
from bot.helpers.billing.main import client


async def update_daily_expenses(date: datetime):
    need_count_server_expenses = True
    need_count_database_expenses = True

    server_transactions = await get_transactions_by_product_id_and_created_time(ServiceType.SERVER, date)
    database_transactions = await get_transactions_by_product_id_and_created_time(ServiceType.DATABASE, date)
    if len(server_transactions) > 0:
        need_count_server_expenses = False
    if len(database_transactions) > 0:
        need_count_database_expenses = False

    if not need_count_server_expenses and not need_count_database_expenses:
        return

    query = f"""
SELECT
  service.description AS service,
  SUM(cost) + IFNULL(SUM((SELECT SUM(amount) FROM UNNEST(credits))), 0) AS total_cost
FROM
  `{config.BILLING_TABLE.get_secret_value()}`
WHERE
  _PARTITIONTIME = TIMESTAMP("{date.strftime("%Y-%m-%d")}")
  AND project.name = 'GPTsTurboBot'
GROUP BY
  service
"""

    query_job = client.query(query)
    server_expenses = 0
    database_expenses = 0

    for row in query_job:
        service = row['service']
        expense = row['total_cost']
        if (
            service == 'Cloud Run' or
            service == 'App Engine' or
            service == 'Compute Engine' or
            service == 'Cloud Logging' or
            service == 'Cloud Scheduler' or
            service == 'Networking'
        ):
            server_expenses += expense
        elif (
            service == 'BigQuery' or
            service == 'Cloud Memorystore for Redis' or
            service == 'Cloud Storage'
        ):
            database_expenses += expense

    if need_count_server_expenses:
        await write_transaction(
            user_id=config.SUPER_ADMIN_ID,
            type=TransactionType.EXPENSE,
            product_id=ServiceType.SERVER,
            amount=round(server_expenses, 4),
            clear_amount=round(server_expenses, 4),
            currency=Currency.USD,
            quantity=1,
            created_at=date,
        )
    if need_count_database_expenses:
        await write_transaction(
            user_id=config.SUPER_ADMIN_ID,
            type=TransactionType.EXPENSE,
            product_id=ServiceType.DATABASE,
            amount=round(database_expenses, 4),
            clear_amount=round(database_expenses, 4),
            currency=Currency.USD,
            quantity=1,
            created_at=date,
        )
