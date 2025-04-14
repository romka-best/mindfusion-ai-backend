from .null_parameter import NullParameter


def true_if_present(value):
    return NullParameter if value is None or value == False else True  # noqa: E712


class Parameters:
    PARAMS_LIST = [
        (true_if_present, "stealth"),
        (true_if_present, "public"),
        (true_if_present, "draft"),
        (int, "iw"),
        (true_if_present, "turbo"),
        (true_if_present, "fast"),
        (true_if_present, "relax"),
        (true_if_present, "video"),
        (str, "niji"),
        (true_if_present, "tile"),
        (int, "sv"),
        (int, "sw"),
        (lambda param: NullParameter if param == [] else tuple(param), "sref"),
        (true_if_present, "raw"),
        (str, "style"),
        (int, "stop"),
        (int, "seed"),
        (str, "profile", "p"),
        (int, "cw"),
        (lambda param: NullParameter if param == [] else tuple(param), "cref"),
        (str, "no"),
        (int, "weired", "w"),
        (str, "version", "v"),
        (int, "stylize", "s"),
        (int, "repeat", "r"),
        (int, "quality", "q"),
        (int, "chaos", "c"),
        (str, "aspect", "ar"),
    ]

    def __init__(self, params: dict):
        for param_type, param_name, *aliases in self.PARAMS_LIST:
            value = self.__get_param_with_fallback(
                params, param_type, param_name, *aliases
            )
            setattr(self, param_name, value)

    def set_param(self, key, value):
        param_type = next(
            (
                param_signature[0]
                for param_signature in self.PARAMS_LIST
                if key in param_signature[1:]
            ),
            str,
        )

        converted_value = self.__convert_to_type(value, param_type)

        setattr(self, key, converted_value)

    def del_param(self, key):
        setattr(self, key, NullParameter)

    def __get_param_with_fallback(self, params: dict, param_type, *keys):
        for key in keys:
            value = params.get(key, NullParameter)
            if value != NullParameter:
                return self.__convert_to_type(value, param_type)

        return NullParameter

    def __convert_to_type(self, value, param_type):
        try:
            return param_type(value)
        except:  # noqa: E722
            return NullParameter

    def to_dict(self):
        return {
            param[1]: getattr(self, param[1])
            for param in self.PARAMS_LIST
            if getattr(self, param[1]) != NullParameter
        }

    def __iter__(self):
        return iter(self.to_dict().items())

    def __getitem__(self, key):
        return getattr(self, key, NullParameter)

    def __setitem__(self, key, value):
        self.set_param(key, value)

    def __contains__(self, key):
        return key in [
            param[1]
            for param in self.PARAMS_LIST
            if getattr(self, param[1]) != NullParameter
        ]

    def __len__(self):
        return len(self.to_dict())

    def __str__(self):
        params_str = []
        for param_name, value in self.to_dict().items():
            if isinstance(value, bool):
                if value:  # If True
                    params_str.append(f"--{param_name}")
            elif isinstance(value, tuple):
                if value:  # If not empty tuple()
                    params_str.append(
                        f"--{param_name} {' '.join(map(str, value))}")
                else:  # If empty tuple() skip
                    next
            else:
                params_str.append(f"--{param_name} {value}")
        return " ".join(params_str)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.to_dict())})"
