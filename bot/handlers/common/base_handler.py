class BaseHandler:
    def __init__(
        self,
        message,
        state,
        lang_code,
        user_id,
        callback_query=None,
        delete_prev_msgs_num=0,
    ):
        self.message = message
        self.state = state
        self.callback_query = callback_query
        self.lang_code = lang_code
        self.user_id = user_id
        self.delete_prev_msgs_num = delete_prev_msgs_num

    @classmethod
    async def create_instance(
        cls,
        message,
        state,
        lang_code,
        user_id,
        callback_query=None,
        delete_prev_msgs_num=0,
        delete_prev_msgs_auto=True,
    ):
        instance = cls(
            message, state, lang_code, user_id, callback_query, delete_prev_msgs_num
        )
        if callback_query:
            await callback_query.answer()

        if delete_prev_msgs_auto and delete_prev_msgs_num:
            await instance._delete_prev_msgs()

        return instance

    # start_msg_id useful when we handle album
    # because in case when we handle album self.message is FIRST uploaded by User
    # in album case, calculation prev msg ids must start from LAST uploaded photo by User
    async def _delete_prev_msgs(self, start_msg_id=None):
        if start_msg_id:
            message_id = start_msg_id
        else:
            message_id = self.message.message_id

        await self.message.bot.delete_messages(
            self.message.chat.id,
            [
                message_id - offset
                for offset in range(0, self.delete_prev_msgs_num)
            ],
        )
        self.delete_prev_msgs_num = 0
