class BaseView:
    plan: list[list[str, dict]]

    def __init__(self):
        self.plan = []

    def plan_add(self, *args):
            self.plan += args

    def render(self):
        raise NotImplementedError

    async def send(self, msg):
        sended_msgs = []

        for action, content in self.plan:
            method = getattr(msg, action)
            sended_msg = await method(**content)
            sended_msgs.append(sended_msg)

        return sended_msgs

    async def send_render(self, msg, *args, **kwargs):
        self.render(*args, **kwargs)

        return await self.send(msg)
