from bot.keyboards.base_view import BaseView

from .edit_btns import EditBtns
from .show import Show


class Edit(BaseView):
    def render(self, product):
        product_info_msg = Show().render(product)[0]
        product_info_msg[1]["reply_markup"] = EditBtns().render(product)[0][1]["reply_markup"]

        self.plan_add(product_info_msg)

        return self.plan

