# MCP Render Server

A small remote [MCP](https://modelcontextprotocol.io) server built with [FastMCP](https://gofastmcp.com),
served over HTTP and deployed on [Render](https://render.com).

| Kind     | Name                                                                        |
|----------|-----------------------------------------------------------------------------|
| Tools    | `add_numbers`, `roll_dice`, `get_datetime`, `fahrenheit_to_celsius`, `reverse_string`, `count_words`, `get_weather` |
| Resource | `local://greeting`                                                          |
| Route    | `GET /health` → `OK` (not protected by the token)                           |

The MCP endpoint is `/mcp`.

## Environment variables

| Variable          | Required | Purpose                                                                 |
|-------------------|----------|-------------------------------------------------------------------------|
| `WEATHER_API_KEY` | for `get_weather` | Free key from [weatherapi.com](https://www.weatherapi.com)     |
| `MCP_API_TOKEN`   | recommended | If set, clients must send `Authorization: Bearer <token>`. Without it anyone with the URL can use the server (and your weather quota). |
| `PORT`            | no       | Set automatically by Render; defaults to `8000` locally                 |

## Run locally

```bash
uv sync
cp .env.example .env    # or create .env by hand with the variables above
uv run main.py          # → http://localhost:8000/mcp
```

Check it is up: `curl http://localhost:8000/health`

## Deploy on Render

1. Push this repo to GitHub.
2. In the Render Dashboard choose **New → Blueprint** and select the repo. Render reads
   [`render.yaml`](render.yaml):
   - build: `uv sync --frozen` (Render adds uv because `uv.lock` is present)
   - start: `uv run --frozen main.py`
   - Python version from `.python-version` (3.12)
3. Enter `WEATHER_API_KEY` when prompted. `MCP_API_TOKEN` is generated for you; copy it from
   the service's **Environment** tab.
4. When the deploy finishes, open `https://<your-service>.onrender.com/health`. It should say `OK`.

On the free plan the service spins down after ~15 minutes idle. The first request after that
takes up to a minute, so open `/health` first to wake it.

## Connect a client

```python
import asyncio
from fastmcp import Client
from fastmcp.client.auth import BearerAuth

async def main():
    async with Client("https://<your-service>.onrender.com/mcp",
                      auth=BearerAuth("<MCP_API_TOKEN>")) as client:
        print([t.name for t in await client.list_tools()])
        print((await client.call_tool("get_weather", {"city": "Lahore"})).data)

asyncio.run(main())
```

## Updating dependencies

```bash
uv add <package>    # updates pyproject.toml and uv.lock
git add pyproject.toml uv.lock && git commit -m "Add <package>"
```

Render builds with `--frozen`, so it installs exactly what is in `uv.lock`. Commit the lock file
whenever it changes.
