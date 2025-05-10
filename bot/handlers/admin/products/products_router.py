from aiogram import Router

from bot.handlers.admin.products.bulk_discount_handler import BulkDiscountHandler
from bot.states.admin.bulk_discount import BulkDiscountState
from bot.states.admin.products import Products
from bot.states.admin.subscriptions_refund import SubscriptionsRefundState
from bot.utils.with_user_language import with_user_language

from .packages_handler import PackagesHandler
from .products_handler import ProductsHandler
from .refund_handler import RefundHandler
from .subscriptions_handler import SubscriptionsHandler

products_router = Router()


@products_router.message(Products.waiting_edit_new_value)
@with_user_language
async def process_new_value(message, state, lang_code, user_id, delete_prev_msgs_num=0):
    data = await state.get_data()
    value = message.text

    handler_class = ProductsHandler
    handler = await handler_class.create_instance(
        message,
        state,
        lang_code=lang_code,
        user_id=user_id,
    )

    await handler.update(
        data.get("product_id"),
        data.get("field_name"),
        value,
        data.get("original_message_id"),
    )


@products_router.message(BulkDiscountState.wait_discount_value)
@with_user_language
async def process_new_discount_value(message, state, lang_code, user_id, delete_prev_msgs_num=0):
    data = await state.get_data()
    value = message.text

    handler_class = BulkDiscountHandler
    handler = await handler_class.create_instance(
        message,
        state,
        lang_code=lang_code,
        user_id=user_id,
    )

    await handler.bulk_discount_update(
        data.get("product_ids"),
        data.get("product_type"),
        value,
    )


@products_router.message(SubscriptionsRefundState.wait_user_id)
@with_user_language
async def process_refund_user_id(message, state, lang_code, user_id, delete_prev_msgs_num=0):
    await (
        await RefundHandler.create_instance(message, state, lang_code=lang_code, user_id=user_id)
    ).show_user_subscriptions(message.text)


async def admin_products_resolver(cq, state, lang_code, user_id, delete_prev_msgs_num=0):
    route = cq.data.split(":")
    # change max_depth when new route sections more
    # admin:product:some_id:some_action is 4 sections 1:2:3:4
    max_depth = 10
    route += [None] * (max_depth - len(route))

    handler_class = None

    match route[1]:
        case "packages":
            handler_class = PackagesHandler
        case "subscriptions":
            handler_class = SubscriptionsHandler

    if "bulk_discount" in [route[2], route[3]]:
        handler_class = BulkDiscountHandler

    if "refund" in [route[2], route[3]]:
        handler_class = RefundHandler

    # fallback
    if handler_class is None:
        handler_class = ProductsHandler

    handler = await handler_class.create_instance(
        cq.message,
        state,
        lang_code,
        user_id,
        callback_query=cq,
        delete_prev_msgs_num=delete_prev_msgs_num,
    )

    match route[0]:
        case "admin":
            match route[1]:
                case "packages":
                    match route[2]:
                        case "index":
                            return await handler.index()
                case "subscriptions":
                    match route[2]:
                        case "index":
                            return await handler.index()
                        case "refund":
                            match route[3]:
                                case "new":
                                    return await handler.new()
                                case "cancel_action":
                                    return await handler.cancel_action()
                    match route[3]:
                        case "refund":
                            match route[4]:
                                case "confirm":
                                    return await handler.confirm(route[2])
                                case "create":
                                    return await handler.create(route[2])
                case "products":
                    match route[2]:
                        case "select_type":
                            return await handler.select_type()
                        case "cancel_update":
                            return await handler.cancel_update()
                        case "bulk_discount":
                            match route[3]:
                                case "ask_value":
                                    return await handler.bulk_discount_ask_value()

                            return await handler.bulk_discount()
                        case "back_to_admin":
                            return await handler.back_to_admin()
                    match route[3]:
                        case "bulk_discount":
                            match route[4]:
                                case "toggle":
                                    return await handler.bulk_discount_toggle(route[2])
                        case "anfv":  # anfv is ask_new_field_value
                            return await handler.ask_new_field_value(route[2], route[4])
                        case "edit":
                            match route[4]:
                                case "desc" | "name" | "price" | "discount":
                                    return await handler.edit(route[2], field=route[4])

                            return await handler.edit(route[2])
                        case "cancel_edit":
                            return await handler.cancel_edit(route[2])
