import logging
import sys

class Colors:
    GRAY = '\033[90m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def setup_logger(log_file='app.log'):
    # Cria um logger
    logger = logging.getLogger(log_file)
    logger.setLevel(logging.DEBUG)  # Define o nível mínimo de log

    # Formato das mensagens de log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Handler para salvar logs em arquivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para exibir logs no terminal com cores
    class ColoredStreamHandler(logging.StreamHandler):
        def emit(self, record):
            try:
                if record.levelno == logging.INFO:
                    msg = Colors.GRAY + record.asctime + \
                        Colors.GREEN + f" {record.levelname} " + \
                            Colors.RESET + record.message
                elif record.levelno == logging.WARNING:
                    msg = Colors.GRAY + record.asctime + \
                        Colors.YELLOW + f" {record.levelname} " + \
                            Colors.RESET + record.message
                elif record.levelno == logging.ERROR or logging.CRITICAL:
                    msg = Colors.GRAY + record.asctime + \
                        Colors.RED + f" {record.levelname} " + \
                            Colors.RESET + record.message
                sys.stdout.write(msg + '\n')
                self.flush()
            except Exception:
                self.handleError(record)

    console_handler = ColoredStreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger