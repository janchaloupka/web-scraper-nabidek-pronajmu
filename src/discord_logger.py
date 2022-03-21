import logging


class DiscordLogger(logging.Handler):
    def __init__(self, client, channel, level) -> None:
        super().__init__(level)
        self.client = client
        self.channel = channel

    def emit(self, record: logging.LogRecord):
        message = "**{}**\n```\n{}\n```".format(record.levelname, record.getMessage())

        self.client.loop.create_task(self.channel.send(message))
