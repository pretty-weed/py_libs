from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import IntEnum
from typing import Self, cast

import requests
from requests.models import Response


class _Phase(IntEnum):
    _disp_char: str

    def __new__(cls, value: int, disp_char: str = "☾"):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj._disp_char = disp_char
        return obj

    def __str__(self) -> str:
        return self._disp_char

    @classmethod
    def members(cls):
        return dict(cls.__members__)

    @classmethod
    def from_usno_name(cls, name: str) -> Self:
        return cls[name.replace(" ", "_").upper()]


class MoonPhase(_Phase):
    # Primary phases, % 2 = 0
    NEW = 0, "🌑"
    NEW_MOON = NEW
    FIRST_QUARTER = 2, "🌓"
    WAXING_HALF = FIRST_QUARTER
    FULL = 4, "🌕"
    FULL_MOON = FULL
    SECOND_QUARTER = 6, "🌗"
    LAST_QUARTER = SECOND_QUARTER
    WANING_HALF = SECOND_QUARTER

    # Secondary phases, % 2 = 1
    WAXING_CRESCENT = 1, "🌒"
    WAXING_GIBBOUS = 3, "🌔"
    WANING_GIBBOUS = 5, "🌖"
    WANING_CRESCENT = 7, "🌘"

    def __str__(self) -> str:
        try:
            return f"{self._disp_char} {self._name_.lower().replace("_", " ")}"
        except AttributeError:
            return f"OOPS: {super().__str__()}"

    @property
    def primary(self) -> bool:
        return self.value % 2 == 0

    @property
    def secondary(self) -> bool:
        return not self.primary

    def next_phase(self) -> Self:
        return self.__class__((self.value + 1) % len(self.__class__))

    def prev_phase(self) -> Self:
        return self.__class__((self.value - 1) % len(self.__class__))

    def primary_or_next(self) -> Self:
        return self if self.primary else self.next_phase()

    def secondary_or_next(self) -> Self:
        return self if self.secondary else self.next_phase()


def get_by_phase(self, key: MoonPhase | int) -> datetime:
    if isinstance(key, int) and not isinstance(key, MoonPhase):

        try:
            key = MoonPhase(key)
        except ValueError as exc:
            raise ValueError(
                f"{key} is not a valid {self.__class__.__name__}"
            ) from exc

    field_name: str = key.name if isinstance(key, _Phase) else key
    res = cast(datetime | None, getattr(self, field_name, None))
    if res is None:
        raise ValueError(
            f"{self} is misconfigured, should not ever return no date for a phase"
        )
    return res


class CalendarFetchError(BaseException):
    def __init__(
        self,
        calendar_url: str,
        response: Response | None,
        msg: str | None = None,
    ) -> None:
        self.response = response
        self.url = calendar_url
        if msg is None:
            msg = f"Failed to fetch calendar from {calendar_url}"
        super().__init__(f"{msg}: {response}")


class _ToBeSet:
    pass


YET_UNSET = _ToBeSet()


@dataclass
class PhaseTime:
    time: datetime
    phase: MoonPhase | _ToBeSet
    cal_time: datetime | None = None

    def with_cal_time(self, cal_time: datetime) -> "PhaseTime":
        return self.__class__(
            time=self.time, phase=self.phase, cal_time=cal_time
        )

    def __str__(self) -> str:
        return f"{str(self.cal_time) + ': ' if self.cal_time is not None else ''}{self.phase} @ {self.time}"


def get_years_between(a: datetime, b: datetime) -> set[int]:
    sy = min(a.year, b.year)
    ey = max(a.year, b.year)
    return set(range(sy, ey + 1))


def _get_year_events(year: int):
    url = f"https://aa.usno.navy.mil/api/moon/phases/year?year={year}"

    try:
        response: Response = requests.get(url)

    except requests.exceptions.RequestException as e:
        raise CalendarFetchError("Error Fetching phases", None) from e

    response.raise_for_status()
    data = response.json()

    if "error" in data:
        raise CalendarFetchError(url, response)

    phasedata = data.get("phasedata", [])
    if not phasedata:
        raise CalendarFetchError(url, response, "No Phase data in response")

    # Parse the API events into exact datetime objects
    events: list[PhaseTime] = []
    for p in phasedata:
        dt = datetime(
            p["year"],
            p["month"],
            p["day"],
            int(p["time"].split(":")[0]),
            int(p["time"].split(":")[1]),
        )
        events.append(PhaseTime(dt, MoonPhase.from_usno_name(p["phase"])))

    # Ensure chronological order
    events.sort(key=lambda x: x.time)
    return events


def get_lunar_calendar(start: datetime, end: datetime):
    """
    Fetches primary phases from the USNO API and calculates
    the transitional secondary phases for every calendar day.
    """

    current_date = start.date()
    end_date = end.date()
    phases: list[PhaseTime] = []
    years = get_years_between(start, end)
    # TOREMOVE once I fix
    if len(years) > 1:
        raise NotImplementedError("Multiyear not implemented yet")
    for year in years:

        events = _get_year_events(year)

        second_offset = timedelta(seconds=1)
        while current_date <= end_date:
            day_start = datetime.combine(current_date, datetime.min.time())

            # 1. Check if a primary phase occurs exactly ON this calendar day
            primary_today: list[PhaseTime] = [
                e for e in events if e.time.date() == current_date
            ]

            if primary_today:
                assert len(primary_today) == 1
                # Primary phases happen at an exact snapshot moment
                phases.append(
                    primary_today[0].with_cal_time(primary_today[0].time)
                )
            elif not phases or phases[-1].phase is YET_UNSET:
                assert all(p.phase is YET_UNSET for p in phases)
                phases.append(
                    PhaseTime(day_start, YET_UNSET, cal_time=day_start)
                )
            else:
                # at least one phase, implicitly, and phases[-1].phase is
                # implicitly not YET_UNSET
                phase_time = (
                    phases[-1].time
                    if not cast(MoonPhase, phases[-1].phase).primary
                    else phases[-1].time + second_offset
                )
                phases.append(
                    PhaseTime(
                        phase_time,
                        cast(MoonPhase, phases[-1].phase).secondary_or_next(),
                        cal_time=day_start,
                    )
                )

            if len(phases) == 1 and phases[0].phase is YET_UNSET:
                # Find the previous phase
                prev_phase: PhaseTime | None = None
                for evt in events:
                    # presuming sorted from above
                    if evt.time > day_start:
                        break
                    elif prev_phase is not None and evt.time < prev_phase.time:
                        raise AssertionError(
                            "Very unexpected that these are unsorted"
                        )
                    else:
                        prev_phase = evt
                if prev_phase is None:
                    # Grab from previous year
                    prev_phase = _get_year_events(start.year - 1)[-1]
                phases[0].time = prev_phase.time + (
                    second_offset
                    if cast(MoonPhase, prev_phase.phase).primary
                    else timedelta(seconds=0)
                )
                phases[0].phase = cast(
                    MoonPhase, prev_phase.phase
                ).secondary_or_next()

            current_date += timedelta(days=1)
            assert not any(pt.cal_time is None for pt in phases)
    return phases
