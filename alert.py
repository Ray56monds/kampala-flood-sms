"""
Kampala Flood Early-Warning SMS System
Fetches rainfall forecast for Kampala flood-prone zones and sends SMS alerts
via Africa's Talking when heavy rain is predicted.
"""

import requests
from datetime import datetime, timezone
import africastalking  # type: ignore
import os
from typing import TypedDict, Any

# ── Configuration ────────────────────────────────────────────────────────────

class Neighbourhood(TypedDict):
    """Type definition for neighbourhood data."""
    name: str
    lat: float
    lon: float
    tip: str

AT_USERNAME = os.getenv("AT_USERNAME", "sandbox")       # Africa's Talking username
AT_API_KEY  = os.getenv("AT_API_KEY", "your_api_key") # Africa's Talking API key
AT_SENDER   = os.getenv("AT_SENDER",   "KampalAlert")  # Sender name (approved by AT)

# Rainfall threshold in mm over the forecast window (3 hours) that triggers alert
ALERT_THRESHOLD_MM = 15.0

# Kampala flood-prone neighbourhoods with their coordinates
NEIGHBOURHOODS: list[Neighbourhood] = [
    {
        "name": "Bwaise",
        "lat": 0.3538,
        "lon": 32.5590,
        "tip": "Avoid Lubigi channel area. Move valuables to higher ground.",
    },
    {
        "name": "Kinawataka",
        "lat": 0.3275,
        "lon": 32.6201,
        "tip": "Avoid low-lying roads near the wetland. Seek higher ground.",
    },
    {
        "name": "Nakivubo",
        "lat": 0.3103,
        "lon": 32.5867,
        "tip": "Stay away from Nakivubo channel. Do not cross flooded roads.",
    },
]

# Test phone numbers (replace with real registered numbers in production)
# In sandbox mode, Africa's Talking only sends to numbers registered in your sandbox
REGISTERED_NUMBERS = {
    "Bwaise":      ["+256700000001", "+256700000002"],
    "Kinawataka":  ["+256700000003", "+256700000004"],
    "Nakivubo":    ["+256700000005", "+256700000006"],
}

# ── Weather fetching ─────────────────────────────────────────────────────────

def get_rainfall_forecast(lat: float, lon: float) -> list[float]:
    """
    Fetch the next 3 hours of hourly precipitation forecast from Open-Meteo.
    Returns a list of precipitation values in mm.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params: dict[str, str | float | int] = {
        "latitude":              lat,
        "longitude":             lon,
        "hourly":                "precipitation",
        "forecast_days":         1,
        "timezone":              "Africa/Kampala",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Find the current hour index
    times = data["hourly"]["time"]
    precip = data["hourly"]["precipitation"]
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00")

    try:
        current_index = times.index(now_str)
    except ValueError:
        # Fall back to first available hour
        current_index = 0

    # Return next 3 hours of forecast
    return precip[current_index : current_index + 3]


def evaluate_risk(forecast_mm: list[float]) -> tuple[bool, float]:
    """
    Evaluate whether the forecast triggers an alert.
    Returns (should_alert, total_mm).
    """
    total = sum(forecast_mm)
    return total >= ALERT_THRESHOLD_MM, round(total, 1)


# ── SMS sending ──────────────────────────────────────────────────────────────

def send_sms_alert(neighbourhood: Neighbourhood, total_mm: float, recipients: list[str]) -> None:
    """
    Send an SMS flood alert to all registered numbers in a neighbourhood.
    """
    africastalking.initialize(AT_USERNAME, AT_API_KEY)  # type: ignore
    sms = africastalking.SMS  # type: ignore

    message = (
        f"⚠️ FLOOD ALERT — {neighbourhood['name']}: "
        f"{total_mm}mm of rain expected in the next 3 hours. "
        f"{neighbourhood['tip']} "
        f"Stay safe. — KampalAlert"
    )

    try:
        response: Any = sms.send(message, recipients, sender_id=AT_SENDER)  # type: ignore
        print(f"[{neighbourhood['name']}] SMS sent → {response}")
    except Exception as e:
        print(f"[{neighbourhood['name']}] SMS failed: {e}")


# ── Main loop ────────────────────────────────────────────────────────────────

def run():
    print(f"\n{'='*55}")
    print(f"  KampalAlert — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*55}")

    for neighbourhood in NEIGHBOURHOODS:
        name = neighbourhood["name"]
        try:
            forecast = get_rainfall_forecast(neighbourhood["lat"], neighbourhood["lon"])
            should_alert, total_mm = evaluate_risk(forecast)

            status = "🔴 ALERT" if should_alert else "🟢 CLEAR"
            print(f"  {name:<15} | {total_mm:>5} mm forecast | {status}")

            if should_alert:
                recipients = REGISTERED_NUMBERS.get(name, [])
                if recipients:
                    send_sms_alert(neighbourhood, total_mm, recipients)
                else:
                    print(f"  {name}: No registered numbers on file.")

        except Exception as e:
            print(f"  {name}: Error — {e}")

    print(f"{'='*55}\n")


if __name__ == "__main__":
    run()
