from __future__ import annotations

from .parameters import Parameters


class Prompt:
    def __init__(
        self,
        reference_images: list[str] | None = None,
        text: str = "",
        params: dict | Parameters = None,
    ):
        if params is None:
            params = {}
        if reference_images is None:
            reference_images = []

        self.reference_images = list(reference_images)
        self.text = str(text)
        self.params = params if isinstance(params, Parameters) else Parameters(params)

    def to_dict(self):
        return {
            "reference_images": self.reference_images,
            "text": self.text,
            "params": repr(self.params),
        }

    def __str__(self):
        return " ".join([" ".join(map(str, self.reference_images)), self.text, str(self.params)]).strip()

    def __repr__(self):
        return f"{self.__class__.__name__}(reference_images={self.reference_images!r}, text={self.text!r}, params={self.params!r})"
