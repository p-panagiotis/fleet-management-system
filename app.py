import logging
import time

from fastapi import FastAPI, Request

from routes.driver import router as driver_router
from routes.car import router as car_router
from routes.trip import router as trip_router

logger = logging.getLogger(__name__)

# instantiate FastAPI
app = FastAPI()


@app.middleware("http")
async def handle_request(request: Request, call_next):
    return await handle_http_middleware(request=request, call_next=call_next)


@app.get("/", tags=["Root"])
async def api_read_root():
    return {"message": "Welcome to Fleet Management System"}


app.include_router(driver_router, tags=["Drivers"], prefix="/drivers")
app.include_router(car_router, tags=["Cars"], prefix="/cars")
app.include_router(trip_router, tags=["Trips"], prefix="/trips")


async def handle_http_middleware(request, call_next):
    # store start request datetime
    start_time = time.time()
    # execute request
    response = await call_next(request)
    # calculate request time in ms
    process_time = (time.time() - start_time) * 1000
    # log request duration
    logger.info(
        f"{request.url.hostname} "
        f"[{request.url.scheme.upper()}/{request.scope.get('http_version')}] "
        f"\"{request.method} {request.url.path}\" "
        f"{response.status_code} "
        f"({'{0:.2f}'.format(process_time)} ms)"
    )
    return response
