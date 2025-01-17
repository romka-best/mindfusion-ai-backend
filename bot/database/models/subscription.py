from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Optional

from bot.database.models.common import Currency, PaymentMethod, Quota


class SubscriptionType(StrEnum):
    MONTHLY = 'MONTHLY'
    YEARLY = 'YEARLY'


class SubscriptionPeriod:
    MONTH1 = 'MONTH_1'
    MONTHS3 = 'MONTHS_3'
    MONTHS6 = 'MONTHS_6'
    MONTHS12 = 'MONTHS_12'


class SubscriptionStatus(StrEnum):
    ACTIVE = 'ACTIVE'
    TRIAL = 'TRIAL'
    WAITING = 'WAITING'
    FINISHED = 'FINISHED'
    DECLINED = 'DECLINED'
    CANCELED = 'CANCELED'
    RESUBSCRIBED = 'RESUBSCRIBED'
    ERROR = 'ERROR'


SUBSCRIPTION_FREE_LIMITS = {
    Quota.CHAT_GPT4_OMNI_MINI: 10,
    Quota.CHAT_GPT4_OMNI: 0,
    Quota.CHAT_GPT_O_1_MINI: 0,
    Quota.CHAT_GPT_O_1: 0,
    Quota.CLAUDE_3_HAIKU: 10,
    Quota.CLAUDE_3_SONNET: 0,
    Quota.CLAUDE_3_OPUS: 0,
    Quota.GEMINI_2_FLASH: 10,
    Quota.GEMINI_1_PRO: 0,
    Quota.GEMINI_1_ULTRA: 0,
    Quota.GROK_2: 0,
    Quota.PERPLEXITY: 0,
    Quota.EIGHTIFY: 1,
    Quota.GEMINI_VIDEO: 1,
    Quota.DALL_E: 0,
    Quota.MIDJOURNEY: 0,
    Quota.STABLE_DIFFUSION_XL: 1,
    Quota.STABLE_DIFFUSION_3: 0,
    Quota.FLUX_1_DEV: 1,
    Quota.FLUX_1_PRO: 0,
    Quota.LUMA_PHOTON: 1,
    Quota.RECRAFT: 0,
    Quota.FACE_SWAP: 0,
    Quota.PHOTOSHOP_AI: 0,
    Quota.MUSIC_GEN: 0,
    Quota.SUNO: 0,
    Quota.KLING: 0,
    Quota.RUNWAY: 0,
    Quota.LUMA_RAY: 0,
    Quota.PIKA: 0,
    Quota.WORK_WITH_FILES: True,
    Quota.ACCESS_TO_CATALOG: False,
    Quota.FAST_MESSAGES: False,
    Quota.VOICE_MESSAGES: False,
}


class Subscription:
    COLLECTION_NAME = 'subscriptions'

    id: str
    user_id: str
    product_id: str
    period: SubscriptionPeriod
    status: SubscriptionStatus
    currency: Currency
    amount: float
    income_amount: float
    payment_method: PaymentMethod
    provider_payment_charge_id: Optional[str]
    provider_auto_payment_charge_id: str
    stripe_id: Optional[str]
    start_date: datetime
    end_date: datetime
    created_at: datetime
    edited_at: datetime

    def __init__(
        self,
        id: str,
        user_id: str,
        product_id: str,
        period: SubscriptionPeriod,
        status: SubscriptionStatus,
        currency: Currency,
        amount: float,
        income_amount=0.00,
        payment_method=PaymentMethod.YOOKASSA,
        provider_payment_charge_id='',
        provider_auto_payment_charge_id='',
        stripe_id=None,
        start_date=None,
        end_date=None,
        created_at=None,
        edited_at=None,
        **kwargs,
    ):
        self.id = str(id)
        self.user_id = str(user_id)
        self.product_id = product_id
        self.period = period
        self.status = status
        self.currency = currency
        self.amount = amount
        self.income_amount = income_amount
        self.payment_method = payment_method
        self.provider_payment_charge_id = provider_payment_charge_id
        self.provider_auto_payment_charge_id = provider_auto_payment_charge_id
        self.stripe_id = stripe_id

        self.start_date = start_date if start_date is not None else datetime.now(timezone.utc)
        if not end_date and period == SubscriptionPeriod.MONTH1:
            self.end_date = self.start_date + timedelta(days=30)
        elif not end_date and period == SubscriptionPeriod.MONTHS3:
            self.end_date = self.start_date + timedelta(days=90)
        elif not end_date and period == SubscriptionPeriod.MONTHS6:
            self.end_date = self.start_date + timedelta(days=180)
        elif not end_date and period == SubscriptionPeriod.MONTHS12:
            self.end_date = self.start_date + timedelta(days=365)
        else:
            self.end_date = end_date

        current_time = datetime.now(timezone.utc)
        self.created_at = created_at if created_at is not None else current_time
        self.edited_at = edited_at if edited_at is not None else current_time

    def to_dict(self):
        return vars(self)
