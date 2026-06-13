# chrischall MCP marketplace

A single Claude Code marketplace bundling Chris Hall's MCP servers. Each plugin lives in its own repo; this catalog just references them.

## Install

```bash
# Add the marketplace once
claude plugin marketplace add chrischall/mcp-marketplace

# Then browse / install any server
/plugin   # interactive picker
# or e.g.
claude plugin install zillow-mcp@chrischall
```

## Servers (28)

### education

- **[Artsonia](https://github.com/chrischall/artsonia-mcp)** (`artsonia-mcp`) — MCP server for Artsonia — access student portfolios, post comments, and manage fans via natural language

### finance

- **[Credit Karma](https://github.com/chrischall/creditkarma-mcp)** (`creditkarma-mcp`) — MCP server for Credit Karma — sync and query your transactions, spending, and accounts via natural language
- **[Splitwise](https://github.com/chrischall/splitwise-mcp)** (`splitwise-mcp`) — MCP server for Splitwise — manage expenses, groups, and friends via natural language

### media

- **[Gemini Images](https://github.com/chrischall/gemini-mcp)** (`gemini-mcp`) — Generate and edit images with Google Gemini image models (Nano Banana / Nano Banana Pro) via natural language prompts

### music

- **[MusicBrainz](https://github.com/chrischall/musicbrainz-mcp)** (`musicbrainz-mcp`) — MCP server for MusicBrainz — search/browse music metadata, fetch cover art, and submit tags, ratings, and collections
- **[setlist.fm](https://github.com/chrischall/setlist-mcp)** (`setlist-mcp`) — MCP server for setlist.fm — search concert setlists, artists, venues, and tours via natural language

### productivity

- **[App Store Connect](https://github.com/chrischall/app-store-connect-mcp)** (`app-store-connect`) — App Store Connect tools for Claude — apps, TestFlight, customer reviews, sales/finance reports, and team users via MCP
- **[apple-mail](https://github.com/chrischall/apple-mail-mcp)** (`apple-mail`) — Manage Apple Mail through natural language - read, search, send, and organize emails
- **[Apple (Swift)](https://github.com/chrischall/apple-swift-mcp)** (`apple-swift-mcp`) — Native Swift MCP server for Apple apps — EventKit/Contacts/MapKit first-party, AppleScript-backed Mail/Messages/Notes. Requires macOS 14+ Apple Silicon.
- **[Canvas LMS](https://github.com/chrischall/canvas-parent-mcp)** (`canvas-parent-mcp`) — Canvas LMS (Instructure) MCP server for Claude — student/observer access via natural language
- **[Compass](https://github.com/chrischall/compass-mcp)** (`compass-mcp`) — MCP server for Compass — search listings, get property details, market reports, saved homes
- **[Etix](https://github.com/chrischall/etix-mcp)** (`etix-mcp`) — MCP server for Etix — search events, venues & performers and fetch event details
- **[Evite](https://github.com/chrischall/evite-mcp)** (`evite`) — Evite tools for Claude — list events, guest lists & RSVPs, RSVP, message guests, and create/edit events via MCP
- **[homes.com](https://github.com/chrischall/homes-mcp)** (`homes-mcp`) — MCP server for homes.com — search listings, get property details, photo galleries, compare properties
- **[HoneyBook](https://github.com/chrischall/honeybook-mcp)** (`honeybook`) — HoneyBook client-portal MCP for Claude — view wedding-vendor contracts and invoices via MCP
- **[Infinite Campus](https://github.com/chrischall/infinitecampus-mcp)** (`infinitecampus-mcp`) — Infinite Campus (Campus Parent) MCP server for Claude — grades, attendance, assignments, messages, and documents via natural language
- **[ioffice-mcp](https://github.com/chrischall/ioffice-mcp)** (`ioffice-mcp`) — MCP server for iOffice — manage buildings, spaces, reservations, visitors, and more via natural language
- **[MuseScore](https://github.com/chrischall/musescore-mcp)** (`musescore-mcp`) — MCP server for MuseScore — search sheet music and read score metadata via your signed-in browser
- **[OurFamilyWizard](https://github.com/chrischall/ofw-mcp)** (`ofw`) — OurFamilyWizard co-parenting tools for Claude — messages, calendar, expenses, and journal via MCP
- **[OneHome](https://github.com/chrischall/onehome-mcp)** (`onehome-mcp`) — MCP server for OneHome (CoreLogic) — search listings, get property details, photos, schools, saved searches
- **[OpenTable](https://github.com/chrischall/opentable-mcp)** (`opentable-mcp`) — OpenTable reservation management for Claude — relays through a companion Chrome extension in your signed-in opentable.com tab.
- **[Redfin](https://github.com/chrischall/redfin-mcp)** (`redfin-mcp`) — MCP server for Redfin — search listings, get property details, market reports, saved homes
- **[Resy](https://github.com/chrischall/resy-mcp)** (`resy-mcp`) — MCP server for Resy — search restaurants, book tables, manage reservations, favorites, and Priority Notify via natural language
- **[SignUpGenius](https://github.com/chrischall/signupgenius-mcp)** (`signupgenius-mcp`) — SignUpGenius MCP server for Claude — sign-ups, slot reports, and groups via natural language. Free or Pro accounts.
- **[Skylight](https://github.com/chrischall/skylight-mcp)** (`skylight-mcp`) — Skylight Calendar MCP server for Claude — family events, chores, and rewards via natural language.
- **[tempo-api-mcp](https://github.com/chrischall/tempo-api-mcp)** (`tempo-api-mcp`) — MCP server for Tempo — manage worklogs, plans, teams, accounts, and projects via natural language
- **[Zillow](https://github.com/chrischall/zillow-mcp)** (`zillow-mcp`) — MCP server for Zillow — search listings, get property details, Zestimate history, saved searches & homes, market reports
- **[Zola](https://github.com/chrischall/zola-mcp)** (`zola`) — Zola wedding planning tools for Claude — vendors, budget, guests, seating, events, registry, inquiries, and more via MCP

## Updating

Plugin versions are pulled from each source repo. To refresh the catalog after publishing a new server, add its entry to `.claude-plugin/marketplace.json` and commit.
