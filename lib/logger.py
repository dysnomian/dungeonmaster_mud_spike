import logging

logging.basicConfig(
    format="\n===============\n%(levelname)s: %(message)s\n===============\n",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
