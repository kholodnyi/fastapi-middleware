import logging

old_factory = logging.getLogRecordFactory()


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.levelname_colon = f'{record.levelname}:'
    return record


logging.setLogRecordFactory(record_factory)

logger = logging.getLogger('fastapi-middleware')
logger.propagate = False

formatter = logging.Formatter('%(levelname_colon)-9s %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.setLevel(logging.INFO)
