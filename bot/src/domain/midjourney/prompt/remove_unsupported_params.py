UNSUPPORTED_PARAMS = ("stealth", "public", "draft",
                      "video", "repeat", "turbo", "fast", "relax")


class RemoveUnsupportedParams:
    @staticmethod
    def execute(prompt):
        for param in UNSUPPORTED_PARAMS:
            prompt.params.del_param(param)
