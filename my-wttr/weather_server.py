from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
from math import floor

LAT = 30.53456262657574
LON = -81.61698829975411

WANTED_ALERTS = {
    "Special Weather Statement",
    "Severe Thunderstorm Warning",
    "Severe Thunderstorm Watch",
    "Tornado Watch",
    "Tornado Warning",
}

def condition_from_code(code: int) -> str:
    if code == 0:
        return "clear"
    if code in (1, 2):
        return "partly-cloudy"
    if code == 3:
        return "cloudy"
    if code in (45, 48):
        return "fog"
    if code in (51, 53, 55, 56, 57):
        return "drizzle"
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return "rain"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "thunderstorm"
    return "unknown"

def emoji_from_condition(condition: str, is_day: bool) -> str:
    if condition == "clear":
        return "☀️" if is_day else "🌙"
    if condition == "partly-cloudy":
        return "⛅" if is_day else "☁️"
    return {
        "cloudy": "☁️",
        "fog": "🌫️",
        "drizzle": "🌦️",
        "rain": "🌧️",
        "snow": "❄️",
        "thunderstorm": "⛈️",
        "unknown": "🌡️",
    }.get(condition, "🌡️")

def ascii_art(condition: str, is_day: bool):
    if condition == "clear":
        if is_day:
            return "\n".join([
                "   \\   /   ",
                "    .-.    ",
                " ― (   ) ― ",
                "    `-’    ",
                "   /   \\   ",
            ])
        else:
            return "\n".join([
                "      _...  ",
                "    .::::.  ",
                "   ::::::'  ",
                "   `::::.   ",
                "     `'::   ",
            ])

    if condition == "partly-cloudy":
        if is_day:
            return "\n".join([
                "   \\  /      ",
                " _ /\"\".-.    ",
                "   \\_(   ).  ",
                "   /(___(__) ",
                "             ",
            ])
        return "\n".join([
            "    _.._     ",
            "  .\"    \".   ",
            "   (   ).    ",
            "  (___(__)   ",
            "             ",
        ])

    art = {
        "cloudy": [
            "             ",
            "     .--.    ",
            "  .-(    ).  ",
            " (___.__)__) ",
            "             ",
        ],
        "fog": [
            "             ",
            " _ - _ - _ - ",
            "  _ - _ - _  ",
            " _ - _ - _ - ",
            "             ",
        ],
        "drizzle": [
            "     .--.    ",
            "  .-(    ).  ",
            " (___.__)__) ",
            "   ' ' ' '   ",
            "   ' ' ' '   ",
        ],
        "rain": [
            "     .--.    ",
            "  .-(    ).  ",
            " (___.__)__) ",
            "   ,',',',   ",
            "   ,',',',   ",
        ],
        "snow": [
            "     .--.    ",
            "  .-(    ).  ",
            " (___.__)__) ",
            "   * * * *   ",
            "    * * *    ",
        ],
        "thunderstorm": [
            "     .--.    ",
            "  .-(    ).  ",
            " (___.__)__) ",
            "    / / /    ",
            "   ,',',',   ",
        ],
        "unknown": [
            "             ",
            "    ???      ",
            "             ",
            "             ",
            "             ",
        ],
    }

    return "\n".join(art.get(condition, art["unknown"]))

def get_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}"
        f"&longitude={LON}"
        "&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,is_day"
        "&temperature_unit=fahrenheit"
        "&wind_speed_unit=mph"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    current = response.json()["current"]

    temp_f = round(current["temperature_2m"])
    feels_like_f = round(current["apparent_temperature"])
    humidity = round(current["relative_humidity_2m"])
    weather_code = int(current["weather_code"])
    wind_mph = float(current["wind_speed_10m"])
    is_day = bool(current["is_day"])

    condition = condition_from_code(weather_code)
    emoji = emoji_from_condition(condition, is_day)

    return {
        "temp_f": temp_f,
        "feels_like_f": feels_like_f,
        "humidity": humidity,
        "condition": condition,
        "emoji": emoji,
        "wind_mph": wind_mph,
        "is_day": is_day,
    }

def get_alerts():
    url = f"https://api.weather.gov/alerts/active?point={LAT},{LON}"
    headers = {"User-Agent": "my-wttr (personal weather service)"}

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    alerts = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        event = props.get("event")
        if event in WANTED_ALERTS and event not in alerts:
            alerts.append(event)

    return alerts

def build_tooltip(temp_f, feels_like_f, humidity, condition, wind_mph, is_day, alerts):
    condition_label = {
        "clear": "Clear",
        "partly-cloudy": "Partly cloudy",
        "cloudy": "Cloudy",
        "fog": "Fog",
        "drizzle": "Drizzle",
        "rain": "Rain",
        "snow": "Snow",
        "thunderstorm": "Thunderstorm",
        "unknown": "Unknown",
    }.get(condition, "Unknown")

    art = ascii_art(condition, is_day)
    wind = floor(wind_mph)

    weather_block = (
        "Jacksonville\n\n"
        f"{art}\n"
        f"{temp_f}°F   {condition_label}\n"
        f"Feels like: {feels_like_f}°F\n"
        f"Humidity: {humidity}%\n"
        f"Wind: {wind} mph"
    )

    if alerts:
        alert_block = "⚠️ Active alerts:\n" + "\n".join(f"• {a}" for a in alerts)
        return f"{alert_block}\n\n{weather_block}"

    return weather_block

def build_payload():
    weather = get_weather()

    try:
        alerts = get_alerts()
    except Exception:
        alerts = []

    text = f"{weather['emoji']} {weather['temp_f']}°F"
    if alerts:
        text = f"⚠️ {text}"

    tooltip = build_tooltip(
        temp_f=weather["temp_f"],
        feels_like_f=weather["feels_like_f"],
        humidity=weather["humidity"],
        condition=weather["condition"],
        wind_mph=weather["wind_mph"],
        is_day=weather["is_day"],
        alerts=alerts,
    )

    return {
        "text": text,
        "tooltip": tooltip,
    }

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/weather":
            self.send_response(404)
            self.end_headers()
            return

        try:
            payload = build_payload()
        except Exception as e:
            payload = {
                "text": "🌡️ Weather unavailable",
                "tooltip": f"Weather service temporarily unavailable.\n\n{e}",
            }

        body = json.dumps(payload).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 9000), Handler)
    print("Weather server running on http://127.0.0.1:9000/weather")
    server.serve_forever()
