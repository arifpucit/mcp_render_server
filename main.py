import random, datetime, os
import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.resources import TextResource
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
from starlette.requests import Request
from starlette.responses import PlainTextResponse

# On your laptop the keys come from a local .env file; on Render they come from the
# service's Environment Variables (a missing .env file is simply ignored).
load_dotenv()
weather_api_key = os.getenv("WEATHER_API_KEY")

# Optional: if MCP_API_TOKEN is set, every request must send "Authorization: Bearer <token>"
api_token = os.getenv("MCP_API_TOKEN")
auth = StaticTokenVerifier(tokens={api_token: {"client_id": "student"}}) if api_token else None

mcp = FastMCP(name="Demo-server", auth=auth)

@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together and return their sum."""
    return a + b

@mcp.tool()
def roll_dice(n_dice: int = 1) -> list[int]:
    """Roll n_dice 6-sided dice and return the result."""
    return [random.randint(1, 6) for _ in range(n_dice)]

@mcp.tool()
def get_datetime() -> str:
    """Return the server's current date and time (UTC on Render) as a string."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def fahrenheit_to_celsius(temp_f: float) -> float:
    """Convert a temperature from Fahrenheit to Celsius."""
    return (temp_f - 32) * 5.0 / 9.0

@mcp.tool()
def reverse_string(text: str) -> str:
    """Reverse the given text string."""
    return text[::-1]

@mcp.tool()
def count_words(text: str) -> int:
    """Count the number of words in a given text string."""
    return len(text.split())

@mcp.tool()
def get_weather(city: str = "Lahore") -> dict:
    """Fetch current weather info for a given city using WeatherAPI.com"""
    if not weather_api_key:
        return {"error": "WEATHER_API_KEY is not set on the server"}
    try:
        url = "https://api.weatherapi.com/v1/current.json"
        response = requests.get(url, params={"key": weather_api_key, "q": city}, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            "Country": data['location']['country'],
            "City": data['location']['name'],
            "Temperature (C)": data['current']['temp_c'],
            "Condition": data['current']['condition']['text'],
            "Humidity (%)": data['current']['humidity'],
            "Wind (km/h)": data['current']['wind_kph'],
            "Last Updated": data['current']['last_updated'],
        }
    except Exception as e:
        return {"error": str(e)}

mcp.add_resource(TextResource(uri="local://greeting", name="greeting",
                              description="A simple greeting message",
                              text="Hello from your remote MCP server on Render! 🎉"))

# A plain web page to check that the service is up (and to wake it after a spin-down).
# Custom routes are not protected by the token.
@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

if __name__ == "__main__":
    # Render tells the app which port to use through the PORT variable (default 10000).
    port = int(os.getenv("PORT", 8000))
    mcp.run(transport="http", host="0.0.0.0", port=port)
