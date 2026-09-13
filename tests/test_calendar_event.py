from portable_agent.models.proposal import CalendarEvent


def test_calendar_event_when_offset_is_set_should_keep_original_text() -> None:
    start = "2026-09-12T10:00:00+03:00"
    end = "2026-09-12T10:30:00+03:00"

    event = CalendarEvent(
        title="Compose check",
        startAt=start,
        endAt=end,
        timeZone="Europe/Moscow",
    )

    assert isinstance(event.start_at, str)
    assert event.start_at == start
    assert event.end_at == end
