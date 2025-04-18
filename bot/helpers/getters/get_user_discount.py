def get_user_discount(
    user_discount: int, subscription_discount: int, product_discount: int
) -> int:
    return max(user_discount, subscription_discount, product_discount)
