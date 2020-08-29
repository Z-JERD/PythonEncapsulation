import os
import time
import logging.config

CONFIG_DICT = {

    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {

        "simple": {
            "format":  "%(asctime)s -%(module)s:%(funcName)s[%(lineno)d] - %(levelname)s: %(message)s"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },

        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "info.log",
            "maxBytes": 1024 * 1024 * 1024,
            "backupCount": 20,
            "encoding": "utf8"
        },

        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "simple",
            "filename":  "error_log",
            "maxBytes": 1024 * 1024 * 1024,
            "backupCount": 20,
            "encoding": "utf8"
        }
    },

    "loggers": {

            "console_handler": {
                "level": "DEBUG",
                "handlers": ["console"]
            },

            "info_handler": {
                "level": "INFO",
                "handlers": ["info_file_handler"]
            },

            "error_handler": {
                "level": "INFO",
                "handlers": ["info_file_handler", "error_file_handler"]
            },

            "all_handler": {
                "level": "DEBUG",
                "handlers": ["console", "info_file_handler", "error_file_handler"]
            }
    }

}


def setup_logging(log_path=None, handler=None):
    """
    :param log_path: 日志地址
    :param handler:
    :return:

    存在 error_file_handler 加载配置时会把error_file_handler对应的文件也会创建
    如果只想生成info文件,就把error_file_handler的配置去掉 同时 loggers相关配置不要出现 error_file_handler
    """

    if not log_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # base_dir = os.getcwd()
        log_path = os.path.join(base_dir, 'logger')

    if not handler:
        handler = "info_handler"

    current_month = time.strftime("%Y%m", time.localtime())

    log_path = os.path.join(log_path, current_month)

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    info_file = os.path.join(log_path, '{date}_info.log'.format(date=time.strftime(
        "%Y%m%d", time.localtime())))

    error_file = os.path.join(log_path, '{date}_error.log'.format(date=time.strftime(
        "%Y%m%d", time.localtime())))

    CONFIG_DICT['handlers']['info_file_handler'].update({
        'filename': info_file
    })

    CONFIG_DICT['handlers']['error_file_handler'].update({
        'filename': error_file
    })

    if handler == "info_handler":

        CONFIG_DICT['handlers'].pop('error_file_handler', None)
        CONFIG_DICT['loggers']['error_handler']['handlers'].remove('error_file_handler')
        CONFIG_DICT['loggers']['all_handler']['handlers'].remove('error_file_handler')

    logging.config.dictConfig(CONFIG_DICT)

    return logging.getLogger(handler)


if __name__ == '__main__':

    logger = setup_logging()

    logger.info("this is a demo")
    logger.error("this is a error")
