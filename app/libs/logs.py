import logging


formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

scheduler_logger = logging.getLogger("main")
scheduler_logger.setLevel(logging.DEBUG)
scheduler_handler = logging.FileHandler("main.log")
scheduler_handler.setLevel(logging.INFO)
scheduler_handler.setFormatter(formatter)
scheduler_logger.addHandler(scheduler_handler)
