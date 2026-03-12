from datetime import date

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.text import Text

from y360_calendar.auth import AuthError, get_token
from y360_calendar.calendar import Event, delete_event, get_today_events, remove_attendee
from y360_calendar.config import AppConfig, config_exists, load_config, save_config

console = Console()


def _prompt_config() -> AppConfig:
    console.print(Panel("First-time setup: enter your Yandex 360 service app credentials", title="Setup"))
    client_id = Prompt.ask("Client ID")
    client_secret = Prompt.ask("Client Secret")
    org_id = Prompt.ask("Organization ID")
    config = AppConfig(client_id=client_id, client_secret=client_secret, org_id=org_id)
    save_config(config)
    console.print("[green]Configuration saved.[/green]\n")
    return config


def _format_time(dt) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%H:%M")


def _display_events(events, email: str) -> None:
    table = Table(title=f"Calendar for {email} — {date.today():%d.%m.%Y}", show_lines=True)
    table.add_column("#", justify="right", style="dim", width=3)
    table.add_column("Start", width=5)
    table.add_column("End", width=5)
    table.add_column("Event", min_width=20)
    table.add_column("Location")

    if not events:
        console.print(Panel("[dim]No events for today.[/dim]", title="Calendar"))
        return

    for i, ev in enumerate(events, 1):
        table.add_row(
            str(i),
            _format_time(ev.start),
            _format_time(ev.end),
            ev.summary,
            ev.location or "—",
        )

    console.print()
    console.print(table)

    _event_detail_loop(events)


def _event_detail_loop(events: list[Event]) -> None:
    while True:
        console.print()
        choice = Prompt.ask(
            f"Enter event number [dim](1–{len(events)})[/dim] for details, or [bold]q[/bold] to quit",
            default="q",
        )
        if choice.strip().lower() == "q":
            break
        try:
            idx = int(choice) - 1
            if not 0 <= idx < len(events):
                raise ValueError
        except ValueError:
            console.print("[red]Invalid number.[/red]")
            continue

        _display_event_detail(events[idx])
        deleted = _edit_menu(events[idx])
        if deleted:
            events.pop(idx)
            console.print("[green]Event deleted.[/green]")
            if not events:
                console.print("[dim]No more events.[/dim]")
                break


def _display_event_detail(event: Event) -> None:
    rows: list[tuple[str, str]] = [
        ("Event", event.summary),
        ("Start", _format_time(event.start)),
        ("End", _format_time(event.end)),
    ]
    if event.location:
        rows.append(("Location", event.location))
    if event.organizer:
        rows.append(("Organizer", event.organizer))
    if event.attendees:
        rows.append(("Attendees", ", ".join(event.attendees)))
    if event.description:
        rows.append(("Description", event.description))
    if event.url:
        rows.append(("URL", event.url))

    table = Table(show_header=False, show_lines=True, title="Event Details", min_width=40)
    table.add_column("Field", style="bold", width=12)
    table.add_column("Value")
    for field, value in rows:
        table.add_row(field, value)

    console.print()
    console.print(table)


def _edit_menu(event: Event) -> bool:
    """Show edit options. Returns True if the event was deleted."""
    console.print()
    choice = Prompt.ask(
        "[bold]e[/bold]dit  /  [bold]b[/bold]ack",
        choices=["e", "b"],
        default="b",
    )
    if choice == "b":
        return False

    console.print()
    action = Prompt.ask(
        "[bold]1[/bold] Delete event  /  [bold]2[/bold] Remove attendee  /  [bold]b[/bold]ack",
        choices=["1", "2", "b"],
        default="b",
    )

    if action == "1":
        confirm = Prompt.ask(
            f"Delete [bold]{event.summary}[/bold]? (y/n)",
            choices=["y", "n"],
            default="n",
        )
        if confirm == "y":
            try:
                delete_event(event)
                return True
            except Exception as exc:
                console.print(f"[red]Failed to delete event:[/red] {exc}")
    elif action == "2":
        _remove_attendee_flow(event)

    return False


def _remove_attendee_flow(event: Event) -> None:
    if not event.attendees:
        console.print("[dim]No attendees on this event.[/dim]")
        return

    while event.attendees:
        table = Table(title="Attendees", show_lines=True)
        table.add_column("#", justify="right", style="dim", width=3)
        table.add_column("Email")
        for i, addr in enumerate(event.attendees, 1):
            table.add_row(str(i), addr)
        console.print()
        console.print(table)

        console.print()
        choice = Prompt.ask(
            f"Select attendee to remove [dim](1–{len(event.attendees)})[/dim], or [bold]b[/bold]ack",
            default="b",
        )
        if choice.strip().lower() == "b":
            break
        try:
            idx = int(choice) - 1
            if not 0 <= idx < len(event.attendees):
                raise ValueError
        except ValueError:
            console.print("[red]Invalid number.[/red]")
            continue

        email_to_remove = event.attendees[idx]
        confirm = Prompt.ask(
            f"Remove [bold]{email_to_remove}[/bold]? (y/n)",
            choices=["y", "n"],
            default="n",
        )
        if confirm == "y":
            try:
                remove_attendee(event, email_to_remove)
                console.print(f"[green]Removed {email_to_remove}.[/green]")
            except Exception as exc:
                console.print(f"[red]Failed to remove attendee:[/red] {exc}")


def main() -> None:
    console.print(Panel("[bold]Y360 Calendar[/bold]", subtitle="Yandex 360 Calendar Viewer"))

    if config_exists():
        config = load_config()
    else:
        config = _prompt_config()

    email = Prompt.ask("User email")

    with console.status("Authenticating..."):
        try:
            token = get_token(config.client_id, config.client_secret, email)
        except AuthError as exc:
            console.print(f"[red]Authentication failed:[/red] {exc}")
            raise SystemExit(1)

    with console.status("Fetching calendar events..."):
        try:
            events = get_today_events(email, token)
        except Exception as exc:
            console.print(f"[red]Failed to fetch events:[/red] {exc}")
            raise SystemExit(1)

    _display_events(events, email)
