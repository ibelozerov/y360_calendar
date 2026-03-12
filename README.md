# Y360 Calendar

TUI application for viewing today's Yandex 360 calendar events.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) package manager
- A Yandex 360 organization with a configured [service application](https://yandex.ru/support/yandex-360/business/admin/ru/security-service-applications)

## Run directly from GitHub

```bash
uvx --from "git+https://github.com/abugrin/y360_calendar" y360-calendar
```

## Install locally

```bash
uv pip install .
y360-calendar
```

Or run without installing:

```bash
uv run y360-calendar
```

## First launch

On the first run the app will prompt for your service application credentials:

- **Client ID** — service app OAuth client id
- **Client Secret** — service app OAuth client secret
- **Organization ID** — your Yandex 360 org id

These are saved to `~/.y360_calendar/config.json` and reused on subsequent runs.

## Usage

After setup, the app asks for a user email and displays today's calendar events in a table.
