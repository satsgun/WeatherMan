# Learnings

Lessons and decisions captured during WeatherMan development.

## Claude
**When do you create CLAUDE.md?**
After the context prompt, before any tasks — so right after you provide the overview, implementation details, and functional details, but before Task 1.
The ideal sequence is:
1. Send context prompt (overview + implementation + functional details)
2. Run /init → generates CLAUDE.md
3. Review and edit CLAUDE.md
4. Start tasks one by one

## CLI / UX

- **Status output goes to stderr.** When `--output json` is used, anything printed to stdout breaks JSON parsing by callers. Status banners ("Fetching weather…") belong on stderr so the stdout stream stays clean.
- **Avoid vendor prefixes in user-facing error messages.** Adding `[WeatherMan]` to error strings is redundant when the CLI name is already in the terminal prompt; it adds noise without clarity.
- **Handle missing optional fields gracefully.** The location header was emitting `"City, "` when a geocoded result had no country. Guard every optional field before interpolating it.

## API / Error Handling

- **Parse API responses at the boundary, raise typed errors.** Wrapping Open-Meteo JSON parsing in dedicated `*_parse` helpers lets the rest of the code stay clean and raises a consistent `*APIError` on malformed payloads, rather than letting `KeyError`/`IndexError` bubble up unexpectedly.
- **Always set HTTP timeouts.** Open API calls without a timeout can hang indefinitely. A short connect + read timeout (e.g. `(5, 10)`) keeps the CLI responsive and testable.

## Input Validation

- **Validate bounded inputs at the CLI layer.** The `--days` flag accepts 1–7 (Open-Meteo's forecast window). Catching out-of-range values early at `argparse` time gives the user a clear message rather than a cryptic API error downstream.

## Testing

- **Mock at the `requests` level, not the module boundary.** Patching `requests.get` rather than high-level helpers keeps tests faithful to the real call path and catches integration issues earlier.
- **CLI tests mock `get_complete_weather` directly.** This isolates output formatting from API plumbing — fast and focused.

