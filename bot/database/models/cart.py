from datetime import datetime, timezone


class CartItem:
    product_id: str
    quantity: int
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        product_id: str,
        quantity: int,
        created_at=None,
        edited_at=None,
        **kwargs,
    ):
        self.product_id = product_id
        self.quantity = quantity

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)


class Cart:
    COLLECTION_NAME = "carts"

    id: str
    user_id: str
    items: list[dict]
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        id: str,
        user_id: str,
        items: list[dict],
        created_at=None,
        edited_at=None,
    ):
        self.id = id
        self.user_id = user_id
        self.items = items

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)
