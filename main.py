import logging

from processos import Processor


def setup_logger():
    """
    Setup basic logger.
    """

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    )

    logging.getLogger("urllib3").setLevel(logging.WARNING)


if __name__ == "__main__":
    setup_logger()
    Processor().process()
