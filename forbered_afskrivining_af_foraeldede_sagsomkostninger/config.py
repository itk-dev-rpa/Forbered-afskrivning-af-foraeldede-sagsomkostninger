"""Framework specific setup"""
SMTP_SERVER = "smtp.aarhuskommune.local"
SMTP_PORT = 25
SCREENSHOT_SENDER = "robot@friend.dk"
MAX_RETRY_COUNT = 3
"""Configuration for the process, where runtime parameters are defined."""
MULTIPROCESSING_CONCURRENCY = 8  # use this many cores
QUEUE_NAME = 'fosa'
