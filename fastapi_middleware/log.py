import logging

logger = logging.getLogger('fastapi-middleware')
logger.propagate = False

formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger.addHandler(handler)
