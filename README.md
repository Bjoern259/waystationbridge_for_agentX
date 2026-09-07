# Waystation Bridge v2

Read-only bridge. The homepage fetches Waystation data server-side, so an external agent only needs to GET one URL.

Start command:
`gunicorn app:app`

Main URL: `/`
Machine-readable URL: `/agent-context`
Health: `/health`
