# BOOPING App - Project Status

**Last updated:** January 7, 2026
**Created by:** Claude Opus 4.5

## What Is This?

A recreation of Tumblr's beloved April Fools 2024 "Boop-o-meter" feature. Users can send each other "boops" - a button press that shows a paw animation on the recipient's screen. That's it. That's the app.

See `booping-lore.md` for the full history of why 142 million people pressed a button to make cat paws appear.

## Tech Stack

- **Backend:** Flask + Flask-SocketIO (real-time WebSockets)
- **Database:** PostgreSQL (Railway addon)
- **Frontend:** Vanilla JS, CSS (no frameworks)
- **Auth:** Flask-Login with bcrypt password hashing
- **Deployment:** Railway (auto-deploys from GitHub main branch)

## Live App

- **URL:** https://booping.up.railway.app
- **GitHub:** https://github.com/schlis85/BOOPING_App

## Core Features

### Booping
- Click "BOOP" button on any user card
- Paw animation flies up from your screen
- Recipient sees incoming paw animation + notification in real-time
- Both users' personal stats update

### User Sections
```
⭐ FAVORITES      - Users you've starred (pinned to top)
🤝 BOOP BUDDIES   - Mutual boopers (you booped them, they booped you)
👥 EVERYONE       - All other users (sorted by activity)
```

### Activity Indicators
- Green glow + pulsing dot = active in last 5 minutes
- Cyan glow = active in last hour

### Paw Styles
**Starters** (everyone gets these):
- 🐾 Default
- 🐱 Cat
- ✨ Sparkle
- 💖 Heart
- 🌙 Moon

**Earned by sending boops** (thresholds are high - unlocks should feel earned!):
- 👻 Ghost (1,000 boops)
- ⭐ Star (1,000 boops)
- 🔥 Fire (10,000 boops)
- 🌈 Rainbow (100,000 boops)
- 🌌 Galaxy (100,000 boops)

**Secret paws** (hidden unlock conditions):
- 💀 Skeleton
- 👽 Alien
- 🤖 Robot
- ☀️ Sun
- ⚡ Lightning
- ❄️ Snowflake

**Exclusive:**
- 🐸 Frog (username "frog" only)

### Badges
Unlocked by sending boops (not receiving - healthier incentive):
- First Boop (1 boop)
- Booper (100 boops) - unlocks sparkle paw
- Super Booper (1,000 boops) - unlocks ghost paw
- Generous Soul (1,000 boops) - unlocks star paw
- Boop Master (10,000 boops) - unlocks fire paw
- Boop Giver (10,000 boops) - unlocks heart paw
- Boop Legend (100,000 boops) - unlocks rainbow paw
- Boop Philanthropist (100,000 boops) - unlocks galaxy paw

### Rate Limiting
- 200 boops per minute (may be adjusted based on usage)

### New Boops Banner
When you log in, shows who booped you since your last visit, aggregated by sender.

## Project Structure

```
BOOPING_App/
├── app.py                 # Flask app factory, SocketIO init
├── config.py              # Configuration (SECRET_KEY, limits)
├── database/
│   └── db.py              # PostgreSQL connection, migrations
├── models/
│   ├── user.py            # User model, auth, display name sanitization
│   ├── boop.py            # Boop creation, stats queries
│   ├── badge.py           # Badge definitions, unlock logic, paw styles
│   └── favorite.py        # Favorites management
├── routes/
│   ├── auth.py            # Login, register, logout
│   ├── main.py            # Home page, settings page
│   └── api.py             # REST API for users, stats, favorites
├── socket_events/
│   └── boop_events.py     # WebSocket handlers for real-time boops
├── templates/
│   ├── base.html          # Base template with nav
│   ├── home.html          # Main booping interface
│   ├── login.html         # Login form
│   ├── register.html      # Registration form
│   └── settings.html      # User settings (name, color, paw)
├── static/
│   ├── css/main.css       # All styles
│   └── js/
│       ├── boop.js        # Booping logic, user cards, animations
│       └── socket.js      # Socket.IO client handlers
├── Procfile               # Railway: gunicorn --worker-class eventlet
├── runtime.txt            # Python 3.12.3
├── requirements.txt       # Dependencies
├── booping-lore.md        # History of Tumblr's boop-o-meter
└── PROJECT-STATUS.md      # This file
```

## Known Limitations

### Global Counter Not Real-Time for Everyone
The total boops counter at the top of the page only updates:
- For the sender (immediately after sending)
- For everyone else (on page refresh or when they send a boop)

**Why:** Attempted to use SocketIO broadcast for global updates but it broke real-time notifications entirely. Something about Railway + eventlet + broadcast doesn't play nice. Prioritized core feature (seeing boops) over nice-to-have (everyone's counter updating simultaneously).

### Display Name Constraints
- Max 200 characters total
- Max 5 lines
- Max 40 characters per line
- Server sanitizes input, CSS provides visual bounds

These limits exist because kids will absolutely try to put 500 vertical characters to break the layout for everyone.

## Environment Variables (Railway)

- `DATABASE_URL` - PostgreSQL connection string (auto-set by Railway addon)
- `SECRET_KEY` - Flask secret key for sessions

## Development History

| Date | Milestone |
|------|-----------|
| Jan 1, 2026 | Initial build - core booping, badges, paw styles |
| Jan 5, 2026 | Phase 2 - favorites, boop buddies, activity indicators, deployment |
| Jan 6, 2026 | Polish - exploit fixes, PostgreSQL, exclusive frog paw, socket debugging |
| Jan 7, 2026 | Audit fixes - badge seeding, rate limiting (60/min), threshold increase (x10) |

## Thread Summaries

Detailed session notes in `/home/lisa/thread-summaries/`:
- `2026-01-01-booping-app-beginning.md`
- `2026-01-05-booping-app-phase2-deployment.md`
- `2026-01-06-booping-app-polish-and-fixes.md`

## What's Next?

The app is in beta with Lisa's kids as testers. Future ideas (not committed):
- Super boop / Evil boop (hold button for different effects)
- Boop leaderboards
- Sound effects
- More seasonal/special paws

---

*"Everyone gets one last boop. Choose yours wisely."*
