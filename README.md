# chrischall MCP marketplace

A single Claude Code marketplace bundling Chris Hall's MCP servers. Each plugin lives in its own repo (or monorepo subpackage); this catalog just references them.

## Install

```bash
claude plugin marketplace add chrischall/mcp-marketplace

/plugin   # interactive picker
# or e.g.
claude plugin install zillow-mcp@chrischall
```

## Servers (71)

### data

- **[FlightAware](https://github.com/chrischall/flightaware-mcp)** (`flightaware-mcp`) — Live flight tracking and aviation data via FlightAware AeroAPI — flights, airports, operators, schedules, and alerts
- **[TripAdvisor](https://github.com/chrischall/tripadvisor-mcp)** (`tripadvisor-mcp`) — TripAdvisor travel data via the Terra API — search hotels, restaurants, and attractions, with details, photos, and reviews
- **[Viator](https://github.com/chrischall/viator-mcp)** (`viator-mcp`) — Search Viator tours, activities and experiences — products, pricing, availability schedules, attractions, and destinations via the Viator Partner API

### education

- **[Artsonia](https://github.com/chrischall/artsonia-mcp)** (`artsonia-mcp`) — MCP server for Artsonia — access student portfolios, post comments, and manage fans via natural language

### finance

- **[Credit Karma](https://github.com/chrischall/creditkarma-mcp)** (`creditkarma-mcp`) — MCP server for Credit Karma — sync and query your transactions, spending, and accounts via natural language
- **[FreshBooks](https://github.com/chrischall/freshbooks-mcp)** (`freshbooks-mcp`) — MCP server for FreshBooks — manage invoices, clients, estimates, and payments via natural language
- **[Splitwise](https://github.com/chrischall/splitwise-mcp)** (`splitwise-mcp`) — MCP server for Splitwise — manage expenses, groups, and friends via natural language

### lifestyle

- **[Untappd](https://github.com/chrischall/untappd-mcp)** (`untappd-mcp`) — MCP server for Untappd — search beers/breweries/venues, read profiles/check-ins/wishlists, and post check-ins, toasts, and comments

### media

- **[Gemini Images](https://github.com/chrischall/gemini-mcp)** (`gemini-mcp`) — Generate and edit images with Google Gemini image models (Nano Banana / Nano Banana Pro) via natural language prompts

### music

- **[MusicBrainz](https://github.com/chrischall/musicbrainz-mcp)** (`musicbrainz-mcp`) — MCP server for MusicBrainz — search/browse music metadata, fetch cover art, and submit tags, ratings, and collections
- **[setlist.fm](https://github.com/chrischall/setlist-mcp)** (`setlist-mcp`) — MCP server for setlist.fm — search concert setlists, artists, venues, and tours via natural language

### other

- **[housecallpro](https://github.com/chrischall/housecallpro-mcp)** (`housecallpro`) — Reads the customer-side Housecall Pro portal over plain HTTPS using the per-document retrieval link your contractor sent you.
- **[kiaaccess](https://github.com/chrischall/kiaaccess-mcp)** (`kiaaccess`) — Vehicle status, location, odometer, EV charge state, and confirm-gated door, climate, and charging commands
- **[remind-mcp](https://github.com/chrischall/remind-mcp)** (`remind-mcp`) — Read Remind classes, chats and messages.
- **[schoolpass](https://github.com/chrischall/schoolpass-mcp)** (`schoolpass`) — Students, arrival/dismissal calendar, pending pickup changes, authorized drivers, dismissal locations, and school info for a parent account
- **[simplepractice](https://github.com/chrischall/simplepractice-mcp)** (`simplepractice`) — Read a SimplePractice Client Portal — appointments, invoices and superbills, documents to sign, and practice announcements. Signs in with the portal's own passwordless emailed link; requests go straight to the portal's JSON:API over your own session.

### productivity

- **[accessoticketing](https://github.com/chrischall/accessoticketing-mcp)** (`accessoticketing`) — Reads accesso Passport mobile-ticket links (the URL a venue emails after a purchase) and returns the order, its admissions, the barcode images and Google Wallet save links. The emailed link is the only credential; no account sign-in is involved.
- **[AllTrails](https://github.com/chrischall/alltrails-mcp)** (`alltrails`) — Unofficial AllTrails tools for Claude — search trails, get details, reviews, photos, and saved lists via MCP
- **[AlphaPortal](https://github.com/chrischall/alphaportal-mcp)** (`alphaportal-mcp`) — MCP server for AlphaPortal school-bus transportation — students, stops, live bus location, and notifications via natural language
- **[Angi](https://github.com/chrischall/angi-mcp)** (`angi-mcp`) — MCP server for Angi — find home-service pros, read ratings and reviews
- **[App Store Connect](https://github.com/chrischall/app-store-connect-mcp)** (`app-store-connect`) — App Store Connect tools for Claude — apps, TestFlight, customer reviews, sales/finance reports, and team users via MCP
- **[apple-mail](https://github.com/chrischall/apple-mail-mcp)** (`apple-mail`) — Manage Apple Mail through natural language - read, search, send, and organize emails
- **[Apple (Swift)](https://github.com/chrischall/apple-swift-mcp)** (`apple-swift-mcp`) — Native Swift MCP server for Apple apps — EventKit/Contacts/MapKit first-party, AppleScript-backed Mail/Messages/Notes, PhotoKit+AppleScript Photos. Requires macOS 14+ Apple Silicon.
- **[Booli](https://github.com/chrischall/booli-mcp)** (`booli`) — Booli.se real estate tools for Claude — search listings, sold prices, areas, and market stats via MCP
- **[Canvas LMS](https://github.com/chrischall/canvas-parent-mcp)** (`canvas-parent-mcp`) — Canvas LMS (Instructure) MCP server for Claude — student/observer access via natural language
- **[Compass](https://github.com/chrischall/compass-mcp)** (`compass-mcp`) — MCP server for Compass — search listings, get property details, market reports, saved homes
- **[Crown Town Compost](https://github.com/chrischall/crowntowncompost-mcp)** (`crowntowncompost-mcp`) — MCP server for the Crown Town Compost customer portal — view pickups and invoices, skip a service, and report a missed collection. Authenticates server-side with a session cookie you already hold, or your own portal username and password.
- **[easyTable](https://github.com/chrischall/easytable-mcp)** (`easytable-mcp`) — MCP server for easyTable — restaurant availability plus create/modify/cancel bookings
- **[Etix](https://github.com/chrischall/etix-mcp)** (`etix-mcp`) — MCP server for Etix — search events, venues & performers and fetch event details
- **[Eventbrite](https://github.com/chrischall/eventbrite-mcp)** (`eventbrite-mcp`) — MCP server for Eventbrite — tickets, orders, organizer data, and public event search. Account tools use a personal API token; discovery search routes through the user's signed-in eventbrite.com tab via the fetchproxy bridge, reusing their authenticated session.
- **[Evite](https://github.com/chrischall/evite-mcp)** (`evite`) — Evite tools for Claude — list events, guest lists & RSVPs, RSVP, message guests, and create/edit events via MCP
- **[GetYourGuide](https://github.com/chrischall/getyourguide-mcp)** (`getyourguide`) — GetYourGuide tours and activities for Claude — search, details, options, and reviews via MCP
- **[gogcli](https://github.com/chrischall/gogcli-mcp/tree/main/packages/gogcli-mcp)** (`gogcli-mcp`) — Google Sheets (and more) for Claude via gogcli — read, write, and manage spreadsheets
- **[gogcli (Classroom)](https://github.com/chrischall/gogcli-mcp/tree/main/packages/gogcli-mcp-classroom)** (`gogcli-mcp-classroom`) — Extended Google Classroom for Claude via gogcli — auth + full Classroom support (courses, rosters, coursework, submissions, announcements, topics, invitations)
- **[gogcli (Docs)](https://github.com/chrischall/gogcli-mcp/tree/main/packages/gogcli-mcp-docs)** (`gogcli-mcp-docs`) — Extended Google Docs for Claude via gogcli — auth + full Docs and comments support
- **[gogcli (Drive)](https://github.com/chrischall/gogcli-mcp/tree/main/packages/gogcli-mcp-drive)** (`gogcli-mcp-drive`) — Extended Google Drive for Claude via gogcli — auth + full Drive support (upload, download, permissions, comments, shared drives)
- **[gogcli (Sheets)](https://github.com/chrischall/gogcli-mcp/tree/main/packages/gogcli-mcp-sheets)** (`gogcli-mcp-sheets`) — Extended Google Sheets for Claude via gogcli — auth + full Sheets support
- **[gogcli (Slides)](https://github.com/chrischall/gogcli-mcp/tree/main/packages/gogcli-mcp-slides)** (`gogcli-mcp-slides`) — Extended Google Slides for Claude via gogcli — auth + full Slides support (create, edit, export, templates, markdown)
- **[Hemnet](https://github.com/chrischall/hemnet-mcp)** (`hemnet`) — Hemnet.se real estate tools for Claude — search, sold prices, listings, and market stats via MCP
- **[homes.com](https://github.com/chrischall/homes-mcp)** (`homes-mcp`) — MCP server for homes.com — search listings, get property details, photo galleries, compare properties
- **[HoneyBook](https://github.com/chrischall/honeybook-mcp)** (`honeybook`) — HoneyBook client-portal MCP for Claude — view wedding-vendor contracts and invoices via MCP
- **[Infinite Campus](https://github.com/chrischall/infinitecampus-mcp)** (`infinitecampus-mcp`) — Infinite Campus (Campus Parent) MCP server for Claude — grades, attendance, assignments, messages, and documents via natural language
- **[ioffice-mcp](https://github.com/chrischall/ioffice-mcp)** (`ioffice-mcp`) — MCP server for iOffice — manage buildings, spaces, reservations, visitors, and more via natural language
- **[Jobber Client Hub](https://github.com/chrischall/jobber-mcp)** (`jobber`) — Read the Jobber Client Hub your home-service providers share with you — appointments, invoices, quotes and requests — via MCP
- **[Microsoft Teams](https://github.com/chrischall/microsoft-teams-mcp)** (`microsoft-teams-mcp`) — MCP server for Microsoft Teams — read your chats, teams, channels, and their currently open messages, via your signed-in browser session
- **[MuseScore](https://github.com/chrischall/musescore-mcp)** (`musescore-mcp`) — MCP server for MuseScore — search sheet music and read score metadata via your signed-in browser
- **[MyAtriumHealth](https://github.com/chrischall/myatriumhealth-mcp)** (`myatriumhealth-mcp`) — Read MyAtriumHealth (Epic MyChart) records — test results, medications, allergies, immunizations, health issues, visits — by relaying requests through the user's signed-in browser tab via the fetchproxy bridge.
- **[My Hot Lunchbox](https://github.com/chrischall/myhotlunchbox-mcp)** (`myhotlunchbox-mcp`) — MCP server for My Hot Lunchbox — school lunch calendar, ordering, and payments. Signs in server-side with the parent account credentials.
- **[Outlook (Microsoft 365)](https://github.com/chrischall/office-outlook-mcp)** (`office-outlook-mcp`) — MCP server for Outlook / Microsoft 365 — read mail, folders, calendar, contacts and tasks, and send mail with confirmation
- **[OurFamilyWizard](https://github.com/chrischall/ofw-mcp)** (`ofw`) — OurFamilyWizard co-parenting tools for Claude — messages, calendar, expenses, and journal via MCP
- **[OneHome](https://github.com/chrischall/onehome-mcp)** (`onehome-mcp`) — MCP server for OneHome (CoreLogic) — search listings, get property details, photos, schools, saved searches
- **[On the Cheap](https://github.com/chrischall/onthecheap-mcp)** (`onthecheap-mcp`) — MCP server for the On the Cheap network — daily event listings with times, prices and venues, plus searchable deals and local guides for 14 US cities
- **[OpenTable](https://github.com/chrischall/opentable-mcp)** (`opentable-mcp`) — OpenTable reservation management for Claude — relays through a companion Chrome extension in your signed-in opentable.com tab.
- **[PickUp Patrol](https://github.com/chrischall/pickuppatrol-mcp)** (`pickuppatrol`) — Read and change your children's school dismissal plans in PickUp Patrol — defaults, day-by-day changes and school cutoff times — via MCP
- **[Redfin](https://github.com/chrischall/redfin-mcp)** (`redfin-mcp`) — MCP server for Redfin — search listings, get property details, market reports, saved homes
- **[Resy](https://github.com/chrischall/resy-mcp)** (`resy-mcp`) — MCP server for Resy — search restaurants, book tables, manage reservations, favorites, and Priority Notify via natural language
- **[SignUpGenius](https://github.com/chrischall/signupgenius-mcp)** (`signupgenius-mcp`) — SignUpGenius MCP server for Claude — sign-ups, slot reports, and groups via natural language. Free or Pro accounts.
- **[Six Flags](https://github.com/chrischall/sixflags-mcp)** (`sixflags`) — Six Flags tools for Claude — live wait times, park hours, shows, and day planning for Carowinds and the whole chain
- **[Skills](https://github.com/chrischall/skill-mcp)** (`skill-mcp`) — Serves a directory of Agent Skills over MCP: list them, load their instructions, read their files, run their declared scripts
- **[Skylight](https://github.com/chrischall/skylight-mcp)** (`skylight-mcp`) — Skylight Calendar MCP server for Claude — family events, chores, and rewards via natural language.
- **[tempo-api-mcp](https://github.com/chrischall/tempo-api-mcp)** (`tempo-api-mcp`) — MCP server for Tempo — manage worklogs, plans, teams, accounts, and projects via natural language
- **[Thumbtack](https://github.com/chrischall/thumbtack-mcp)** (`thumbtack`) — Unofficial Thumbtack tools for Claude — search local service pros, read profiles, ratings and reviews via MCP
- **[Tock](https://github.com/chrischall/tock-mcp)** (`tock-mcp`) — Tock (exploretock.com) restaurant discovery for Claude — relays through a companion Chrome extension in your signed-in exploretock.com tab.
- **[Vibo](https://github.com/chrischall/vibo-mcp)** (`vibo-mcp`) — MCP server for Vibo — browse & manage events, timeline, songs, the DJ song ideas/questions, guests, and exports to Spotify/Apple Music
- **[Workday](https://github.com/chrischall/workday-mcp)** (`workday-mcp`) — Read-only MCP server for Workday — fetch tasks, pay, benefits and compensation through your signed-in session
- **[Zillow](https://github.com/chrischall/zillow-mcp)** (`zillow-mcp`) — MCP server for Zillow — search listings, get property details, Zestimate history, saved searches & homes, market reports
- **[Zola](https://github.com/chrischall/zola-mcp)** (`zola`) — Zola wedding planning tools for Claude — vendors, budget, guests, seating, events, registry, inquiries, and more via MCP

### shopping

- **[Groupon](https://github.com/chrischall/groupon-mcp)** (`groupon-mcp`) — MCP server for Groupon — search and browse local, goods, and travel deals via natural language

### sports

- **[MaxPreps](https://github.com/chrischall/maxpreps-mcp)** (`maxpreps-mcp`) — MCP server for MaxPreps — read any US high school's team schedules, scores, records, rosters, stat leaders and athlete careers. Reads the site's public server-rendered data; no account or API key.
- **[Myers Park Athletic Zone](https://github.com/chrischall/myersparkathleticzone-mcp)** (`myersparkathleticzone-mcp`) — MCP server for Myers Park HS athletics — schedules, teams, rosters, coaches, news and broadcast links. Reads the public site's server-rendered pages; no account or credentials required.

### utilities

- **[SimpliSafe](https://github.com/chrischall/simplisafe-mcp)** (`simplisafe-mcp`) — MCP server for SimpliSafe — check system state and sensors, review events, arm/disarm, control smart locks

## Regenerating

The manifest is generated from each source repo's own `marketplace.json`, read from the repo's default branch on GitHub (needs an authenticated `gh`):

```bash
python3 scripts/regen.py
# a listed plugin that disappeared fails the run; if intended:
python3 scripts/regen.py --allow-removal <plugin-name>
```

The `regen` workflow runs this daily and opens a PR when the catalog has drifted. The server list above is rewritten by the same script.

Monorepos (e.g. `gogcli-mcp`) are handled automatically — each subpackage with its own `.claude-plugin/marketplace.json` becomes its own entry via a `git-subdir` source.
