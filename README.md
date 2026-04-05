# 🌧 KampalAlert — Kampala Flood Early-Warning SMS System

A lightweight, automated flood alert system that fetches real-time rainfall forecasts for Kampala's most flood-prone neighbourhoods and sends plain-text SMS warnings to registered residents — **no smartphone or internet required**.

Built for the [Climate Change-Makers Challenge 2026](https://one4earth.org/) by One4Earth × Youth Impact Challenge.

---

## The Problem

Kampala floods regularly. Neighbourhoods like **Bwaise, Kinawataka, and Nakivubo** sit in low-lying areas that flood within minutes of heavy rain. These are also the city's most economically vulnerable communities. The weather data to predict these floods already exists — but it never reaches the people who need it most, because most early-warning systems assume smartphones or internet access.

**Over 60% of Ugandans rely on basic (feature) phones.** A flood warning locked behind an app is no warning at all.

---

## How It Works

```
Open-Meteo API → Rainfall forecast → Threshold check → Africa's Talking SMS → Residents
```

1. Fetches hourly precipitation forecast for each neighbourhood via [Open-Meteo](https://open-meteo.com/) (free, no API key needed)
2. If forecast rainfall exceeds **15mm in the next 3 hours**, an alert is triggered
3. Plain-text SMS is sent to all registered numbers in that neighbourhood via [Africa's Talking](https://africastalking.com/)
4. A live web dashboard shows neighbourhood risk levels (🟢 Clear / 🟡 Watch / 🔴 Alert)

### Sample SMS

```
⚠️ FLOOD ALERT — Bwaise: 18.4mm of rain expected in the next 3 hours.
Avoid Lubigi channel area. Move valuables to higher ground. Stay safe. — KampalAlert
```

---

## Project Structure

```
kampala-flood-sms/
├── alert.py          # Core Python alert script (runs on a scheduler)
├── dashboard.html    # Live web dashboard (no backend needed)
├── requirements.txt  # Python dependencies
└── README.md
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set environment variables

```bash
export AT_USERNAME="your_africastalking_username"
export AT_API_KEY="your_africastalking_api_key"
export AT_SENDER="KampalAlert"
```

> For testing, use `AT_USERNAME=sandbox` and your Africa's Talking sandbox API key.

### 3. Run the alert script

```bash
python alert.py
```

### 4. Schedule it (Linux cron — runs every hour)

```bash
0 * * * * /usr/bin/python3 /path/to/alert.py >> /var/log/kampalert.log 2>&1
```

### 5. Open the dashboard

Just open `dashboard.html` in a browser — it fetches live data directly from Open-Meteo with no backend needed.

Or deploy to GitHub Pages / Vercel for a public URL.

---

## APIs Used

| API | Purpose | Cost |
|-----|---------|------|
| [Open-Meteo](https://open-meteo.com/) | Hourly rainfall forecast | Free, no key |
| [Africa's Talking](https://africastalking.com/) | SMS delivery | Free sandbox; ~$0.003/SMS live |

---

## Neighbourhoods Monitored

| Neighbourhood | Coordinates | Key Risk Area |
|---|---|---|
| Bwaise | 0.3538°N, 32.5590°E | Lubigi channel |
| Kinawataka | 0.3275°N, 32.6201°E | Wetland low-roads |
| Nakivubo | 0.3103°N, 32.5867°E | Nakivubo channel |

---

## Roadmap

- [ ] Luganda-language SMS alerts
- [ ] Opt-in registration via USSD shortcode
- [ ] Integration with KCCA flood response teams
- [ ] Historical flood data for threshold calibration
- [ ] Expand to Jinja, Mbale, Masaka

---

## License

MIT — free to use, adapt, and deploy for any community.
