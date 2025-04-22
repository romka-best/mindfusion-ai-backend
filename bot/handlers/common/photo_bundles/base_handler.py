from aiogram.exceptions import TelegramBadRequest


class BaseHandler:
    def __init__(self, message, state, callback_query=None):
        self.message = message
        self.state = state
        self.callback_query = callback_query

    @classmethod
    async def create_instance(
        cls,
        message,
        state,
        callback_query=None,
        delete_prev_msg=True,
        delete_prev_media=False,
        prev_media_num=None,
        prev_media_offset=1,
    ):
        instance = cls(message, state, callback_query)

        if delete_prev_msg:
            await instance._delete_prev_msg()
        if delete_prev_media:
            await instance._delete_prev_media(prev_media_num, prev_media_offset)

        return instance

    async def _delete_prev_msg(self):
        await self.message.delete()

    async def _delete_prev_media(self, prev_media_num=None, prev_media_offset=1):
        bot = self.message.bot

        if prev_media_num:
            delete_msg_ids = [
                self.message.message_id - i
                for i in range(prev_media_offset, prev_media_offset + prev_media_num)
            ]
            await bot.delete_messages(self.message.chat.id, delete_msg_ids)
        else:
            try:
                temp_msg = await bot.send_message(
                    chat_id=self.message.chat.id,
                    text=".",
                    reply_to_message_id=self.message.message_id - prev_media_offset,
                )
            except TelegramBadRequest:
                return

            media_msg = temp_msg.reply_to_message
            await temp_msg.delete()
            if media_msg.photo:
                await media_msg.delete()
                if media_msg.media_group_id:
                    prev_media_offset += 1

                    while True:
                        bot.delete_messages(
                            self.message.chat.id,
                            [self.message.message_id - prev_media_offset],
                        )

                        try:
                            temp_msg = await bot.send_message(
                                chat_id=self.message.chat.id,
                                text=".",
                                reply_to_message_id=self.message.message_id
                                - prev_media_offset,
                            )
                        except TelegramBadRequest:
                            break

                        media_msg = temp_msg.reply_to_message

                        if not media_msg.media_group_id:
                            break

                        await temp_msg.delete()
                        await media_msg.delete()
                        prev_media_offset += 1
