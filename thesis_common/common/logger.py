"""
Logger to use when logging events used when doing experiments (i.e. events of interest to the thesis, and not
some technical issues, like exceptions).
"""
import logging
thesis_logger_name = 'thesis_logger'
thesis_logger = logging.getLogger(thesis_logger_name)
s = '%(asctime)s %(filename)s:%(module)s %(levelname)s:%(name)s %(message)s'
formatter = logging.Formatter(s)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
thesis_logger.addHandler(handler)
thesis_logger.setLevel(logging.DEBUG)
