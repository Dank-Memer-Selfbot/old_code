import os, uvicorn, pathlib
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from rich.console import Console

# --- Constants --- #

frontend = pathlib.Path(__file__).parent.parent.joinpath("frontend")
templates = Jinja2Templates(directory=frontend.joinpath("templates"))


async def not_found(request, exception):
    return templates.TemplateResponse("404.html", {"request": request})


exception_handlers = {
    404: not_found,
}
app = FastAPI(exception_handlers=exception_handlers)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
console = Console()
apps = []

# --- Import API Routes --- #
for route in [file[:-3] for file in os.listdir("./routes") if file.endswith(".py")]:
    exec("from routes.{} import app as route".format(route))
    exec("apps.append(route)")
    exec("del route")

for route in apps:
    app.include_router(route)
    console.log("[API] Loaded route: {}".format(route))

# --- Events --- #


@app.on_event("startup")
async def startup():
    console.log("[API] Starting...")


@app.on_event("shutdown")
async def shutdown():
    console.log("[API] Shutting down...")


# --- Home --- #


@app.get("/")
async def home():
    return RedirectResponse("/frontend/")


@app.get("/favicon.ico")
async def favicon():
    """Return favicon."""
    return RedirectResponse("/static/favicon.jpg")


# --- Running --- #

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=80, reload=True)
