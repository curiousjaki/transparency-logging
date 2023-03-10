import logging
import sys
from opentelemetry import trace

TILT_LOG_FORMAT = str({
    "timestamp": "%(asctime)s",
    "case:concept:name":"%(case_concept_name)s",
    "concept:name": "%(concept_name)s",
    "message": "%(message)s",
    "tilt": "%(tilt)s"
})
TILT_LOG_DEFAULTS = {
    "message": None,
}

class TiltLogger:
    def __init__(self,log_name) -> None:
        self.logger : logging.Logger = logging.getLogger(log_name)
        formatter = logging.Formatter(fmt=TILT_LOG_FORMAT, defaults=TILT_LOG_DEFAULTS,
                                  datefmt=logging.Formatter.default_msec_format)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.INFO)
        self.tracer = trace.get_tracer(__name__)

    def log(self,concept_name: str,tilt: dict, msg: str ,level: int = logging.INFO):
        def inner_func(original_function):
            def tilt_logging(*args,**kwargs):
                with self.tracer.start_as_current_span(concept_name) as span:
                    self.logger.log(level = level, msg = msg, extra = {
                        "case_concept_name": hex(span.get_span_context().trace_id),
                        "concept_name": concept_name,
                        "tilt": tilt
                        })
                    return original_function(*args,**kwargs)
            return tilt_logging
        return inner_func