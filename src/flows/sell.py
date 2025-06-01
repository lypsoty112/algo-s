from typing import List
from src.broker.alpaca import client
from alpaca.trading.models import Position, Order
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, QueryOrderStatus, OrderType
from src.core.logger import default_logger as logger
from alpaca.trading.requests import GetOrdersRequest
from datetime import datetime as dt
from src.core.config import app_settings


def sell_order(
    position: Position,
):
    logger.info(
        f"Creating sell order for {position.symbol} with quantity {position.qty}"
    )
    order_data: MarketOrderRequest = MarketOrderRequest(
        symbol=position.symbol,
        qty=position.qty,
        side=OrderSide.SELL,
        type=OrderType.MARKET,
    )

    order = client.submit_order(order_data)
    logger.info(f"Sell order submitted successfully for {position.symbol}: {order.id}")


async def sell_flow():
    # Get the current open positions

    positions: List[Position] = client.get_all_positions()
    await logger.ainfo(f"Found {len(positions)} open positions")

    # Get the corresponding buy order for each position
    request_params = GetOrdersRequest(
        status=QueryOrderStatus.CLOSED,
        side=OrderSide.BUY,
        symbol=[pos.symbol for pos in positions],
    )

    orders: List[Order] = client.get_orders(request_params)

    # Sort orders by submitted_at and take the latest one for each position
    orders.sort(key=lambda order: order.submitted_at, reverse=True)

    # Get the latest order for each position
    latest_orders = {order.symbol: order for order in orders}

    # Get the current datetime (UTC-sensitive)
    current_datetime = dt.now(dt.timezone.utc)

    # If an order is older than max working days, has a higher profit than max profit, or has a lower loss than max loss, sell it
    for position in positions:
        # Check for data using the corresponding buy order
        if (
            current_datetime - latest_orders[position.symbol].submitted_at
        ).days > app_settings.MAX_DAYS_IN_POSITION:
            await logger.ainfo(
                f"Selling {position.symbol} because it is older than {app_settings.MAX_DAYS_IN_POSITION} days"
            )
            sell_order(position)

        elif position.unrealized_plpc > app_settings.MAX_PROFIT:
            await logger.ainfo(
                f"Selling {position.symbol} because it has a profit higher than {app_settings.MAX_PROFIT} ({position.unrealized_plpc})"
            )
            sell_order(position)

        elif position.unrealized_plpc < app_settings.MAX_LOSS:
            await logger.ainfo(
                f"Selling {position.symbol} because it has a loss lower than {app_settings.MAX_LOSS} ({position.unrealized_plpc})"
            )
            sell_order(position)
