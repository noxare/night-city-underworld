# Local developer dashboard

Open http://127.0.0.1:8765 on the Windows gaming PC. The dashboard refreshes every
two seconds and reads the authoritative SQLite journal without writing to it.
It displays worker heartbeat, latest bridge response, contacts grouped by save
context, reputation and the last 100 stored events with their consequences.
Filter the journal by NPC, kind or event ID. Missing/unavailable data and stale
heartbeats are shown explicitly. Stored events do not yet have timestamps;
their sequence is database insertion order.

The contact list currently contains synthetic test contacts, not scanned game
NPCs. Campaign synchronization and genuine NPC registration remain separate work.
No bridge requests are sent by this dashboard. It binds only to 127.0.0.1:8765.

After reboot use `%LOCALAPPDATA%\NightCityUnderworld\Open-UnderworldDashboard.cmd`.
The dashboard and bridge are separate processes; use the existing bridge start
helper if its status is offline. No game restart or CET reload is needed to view
the dashboard. Installation verifies local HTTP responses separately from visual QA.
