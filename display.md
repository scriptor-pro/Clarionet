Display (Station & Metadata)

## What this covers
- Station name line (current station label) and metadata line (track/artist label) shown in the center “now playing” box.
- How they size, align, and scroll when text is long.

## Current layout
- Two rows of equal dimensions, stacked vertically inside `station_display` (a GTK Box).
- Top row: `Gtk.Label` wrapped in a `Gtk.ScrolledWindow` (station name).
- Bottom row: `Gtk.DrawingArea` rendered with Cairo/Pango (metadata), so text length never affects GTK size negotiation.
- Both rows have a fixed height of 48px and do not expand vertically; the window height is fixed elsewhere, so these rows keep their height even when text changes.
- The now-playing box does not hexpand; it keeps its set width to reduce layout recalcs.
- The container is non-homogeneous, so each row keeps its own size rather than sharing space.
- Padding: 10px on all sides of the now-playing box; metadata row also has a 10px top margin to sit in the lower half.
- Divider: dotted black separator between rows to visually split station and metadata lines.
- The now-playing box is non-expanding vertically and height-clamped (>=140px) to avoid layout jitter.

## Behavior
- Station name (top row)
  - Center-aligned vertically at all times.
  - Shows the selected station name when idle.
- Metadata (bottom row)
  - Starts blank by default and stays visible (never hidden), avoiding layout jumps.
  - When `media-title` is meaningful, text updates and marquee scheduling runs.
  - When metadata is absent or not meaningful, text resets to blank, marquee is cleared, and alignment recenters the station row.
- Marquee
  - Triggered when metadata overflows the available width (i.e., when the last full character cannot fit).
  - First marquee runs immediately and should scroll fluidly and consistently.
  - The marquee continues until the last character exits left, then the display returns to the truncated start state.
  - The marquee runs once per metadata update.
  - Short metadata stays static (no marquee).

## Key implementation details (for quick reference)
- Fixed heights: station scroller and metadata drawing area both use `set_size_request(..., 48)` and do not expand vertically.
- Station scroller content size is locked with `set_min_content_width`/`set_min_content_height` to prevent long station names from influencing layout.
- Metadata is drawn in `on_track_draw` using Cairo/Pango; scrolling is driven by a timer that advances `track_scroll_offset` once.
- Packing: `pack_start(..., expand=False, fill=False, padding=0)` to lock heights.
- Alignment tweaks happen via `update_display_alignment(has_metadata)`; only adjusts vertical alignment.
- Marquee control: station row uses `_wrap_marquee_label`/`update_marquee`; metadata row uses the Cairo drawing path.
- Padding: 10px margins on the now-playing box; metadata row has an extra 10px top margin to bias it to the lower half.
- Divider: dotted black separator between rows to visually separate the two lines.
- Width: fixed to the content width via GTK size request; horizontally centered and does not hexpand.
- The now-playing box is non-expanding vertically and height-clamped (>=140px) to avoid layout jitter.
- Scrollers disable natural-size propagation to prevent long text from influencing container sizing.

## Known quirks
- If text is extremely tall (unusual fonts or embedded markup), it could clip because height is fixed. Current font is a segmented, single-line style, so this is unlikely.
- Window size is fixed elsewhere; display rows won’t resize the window, but very long text will scroll rather than wrap.

## Ideas for improvement
- Make the fixed height a named constant (e.g., `DISPLAY_ROW_HEIGHT`) to tune easily.
- Add a character-fit threshold before marquee: only start scrolling when a full character no longer fits; keep static otherwise.
- Optional: pause marquee on hover for readability; resume on leave.
