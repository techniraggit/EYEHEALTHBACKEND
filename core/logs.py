from datetime import datetime


class Logger:
    def __init__(self, file_name):
        self.file_name = file_name

    def _get_current_time(self):
        return datetime.now().strftime("%b %d, %Y, %A at %I:%M %p")

    def _write_log(self, level, msg):
        current_time = self._get_current_time()
        with open(f"logs/{self.file_name}", "a") as file:
            file.write(f"{current_time} - [{level}] - {msg}\n")

    def info(self, msg):
        self._write_log("INFO", msg)

    def warning(self, msg):
        self._write_log("WARNING", msg)

    def warn(self, msg):
        self._write_log("WARN", msg)

    def error(self, msg):
        self._write_log("ERROR", msg)


# logger = Logger("crips.log")
# logger.info("we testing here")
# logger.warn("we want to warn you")
