import requests
from datetime import datetime

# Coordinates for each location (name, latitude, longitude)
locations = [
    ("West Texas", 31.8, -102.4),
    ("North Hub (TX)", 32.7, -96.7),
    ("Athos Area", 33.756119, -115.346811),
]

message_lines = []

# Title
message_lines.append("☀️ **7-Day Weather Outlook** ☀️")
message_lines.append("")

def f_to_c(f):
    return round((f - 32) * 5 / 9)

for loc_name, lat, lon in locations:
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max"
        f"&forecast_days=7"
        f"&temperature_unit=fahrenheit"
    )

    response = requests.get(url)
    data = response.json()

    days = data["daily"]["time"]
    temps_high = data["daily"]["temperature_2m_max"]
    temps_low = data["daily"]["temperature_2m_min"]
    codes = data["daily"]["weathercode"]
    precip_probs = data["daily"]["precipitation_probability_max"]

    # Location header
    message_lines.append(f"**{loc_name}**")

    for i in range(7):
        date_obj = datetime.fromisoformat(days[i])
        weekday = date_obj.strftime("%a")
        date_label = date_obj.strftime("%b %d")

        high_f = round(temps_high[i])
        low_f = round(temps_low[i])
        high_c = f_to_c(high_f)
        low_c = f_to_c(low_f)

        code = codes[i]
        rain_pct = precip_probs[i]

        # Weather interpretation (WMO / Open‑Meteo)
        if code == 0:
            icon, desc = "☀️", "Clear skies"
        elif code == 1:
            icon, desc = "🌤️", "Mainly clear"
        elif code == 2:
            icon, desc = "⛅", "Partly cloudy"
        elif code == 3:
            icon, desc = "☁️", "Overcast"
        elif code in (45, 48):
            icon, desc = "🌫️", "Fog"
        elif 51 <= code <= 57:
            icon, desc = "🌦️", "Drizzle"
        elif 61 <= code <= 67:
            icon, desc = "🌧️", "Rain"
        elif 71 <= code <= 77:
            icon, desc = "❄️", "Snow"
        elif 80 <= code <= 82:
            icon, desc = "🌧️", "Rain showers"
        elif 85 <= code <= 86:
            icon, desc = "❄️", "Snow showers"
        elif 95 <= code <= 99:
            icon, desc = "⛈️", "Thunderstorms"
        else:
            icon, desc = "🌤️", "Mixed conditions"

        rain_text = f" ({rain_pct}% chance of rain)" if rain_pct >= 5 else ""

        message_lines.append(
            f"\n⠀\n• {weekday} ({date_label}): "
            f"\n**H**: {high_f}°F/{high_c}°C    |    **L**: {low_f}°F/{low_c}°C – "
            f"{icon} {desc}{rain_text}"
        )

    message_lines.append("")

# Final message
message_text = "\n".join(message_lines)

# Send to Power Automate webhook
import os
webhook_url = os.environ['PA_WEBHOOK_URL']

response = requests.post(webhook_url, json={"text": message_text})

print(f"Posted to Teams, status code: {response.status_code}")
