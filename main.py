import logging
import sys

import uvicorn
from decouple import config

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

HOST = config("HOST")
PORT = int(config("PORT"))

if __name__ == "__main__":
    logger.info(f"Server listening on http://{HOST}:{PORT}")
    uvicorn.run(app="app:app", host=HOST, port=PORT, log_level=logging.WARNING)
