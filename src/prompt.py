from dataclasses import dataclass


@dataclass
class Prompt:
    title: str
    prefix: str
    suffix: str
    url: str
