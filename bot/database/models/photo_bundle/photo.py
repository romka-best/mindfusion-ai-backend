from dataclasses import dataclass


@dataclass
class Photo:
    id: int
    tg_id: str
    file_format: str

    @property
    def file_name(self) -> str:
        return f"{self.id}_{self.tg_id}.{self.file_format}"
