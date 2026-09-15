from _typeshed import Incomplete
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from requests.models import Response
from typing import Self

class _Phase(IntEnum):
    def __new__(cls, value: int, disp_char: str): ...
    @classmethod
    def members(cls): ...
    @classmethod
    def from_usno_name(cls, name: str) -> Self: ...

class MoonPhase(_Phase):
    NEW = (0, "🌑")
    NEW_MOON = NEW
    FIRST_QUARTER = (2, "🌓")
    WAXING_HALF = FIRST_QUARTER
    FULL = (4, "🌕")
    FULL_MOON = FULL
    SECOND_QUARTER = (6, "🌗")
    LAST_QUARTER = SECOND_QUARTER
    WANING_HALF = SECOND_QUARTER
    WAXING_CRESCENT = (1, "🌒")
    WAXING_GIBBOUS = (3, "🌔")
    WANING_GIBBOUS = (5, "🌖")
    WANING_CRESCENT = (7, "🌘")
    @property
    def primary(self) -> bool: ...
    @property
    def secondary(self) -> bool: ...
    def next_phase(self) -> Self: ...
    def prev_phase(self) -> Self: ...
    def primary_or_next(self) -> Self: ...
    def secondary_or_next(self) -> Self: ...

def get_by_phase(self, key: MoonPhase | int) -> datetime: ...

class CalendarFetchError(BaseException):
    response: Incomplete
    url: Incomplete
    def __init__(
        self,
        calendar_url: str,
        response: Response | None,
        msg: str | None = None,
    ) -> None: ...

class _ToBeSet: ...

YET_UNSET: Incomplete

@dataclass
class PhaseTime:
    time: datetime
    phase: MoonPhase | _ToBeSet
    cal_time: datetime | None = ...
    def with_cal_time(self, cal_time: datetime) -> PhaseTime: ...

def get_years_between(a: datetime, b: datetime) -> set[int]: ...
def get_lunar_calendar(start: datetime, end: datetime): ...
