import functools
import inspect
import logging
import types
from pathlib import Path
from time import localtime, strftime

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def make_log_file():
    log_path = Path(__file__).parent / f'logs' / f'{strftime("%Y_%m", localtime())}'

    if not log_path.is_dir():
        log_path.mkdir(parents=True, exist_ok=True)

    log_file = log_path / Path(f'{strftime("%m_%d_%H-%M", localtime())}.log')

    log_formatter = logging.Formatter(
        "%(levelname)s | %(asctime)s | Module: %(module)s | Line: %(lineno)d \n \t"
        " :: %(message)s ::"
    )

    file_handler = logging.FileHandler(f'{log_file}')
    file_handler.setFormatter(log_formatter)

    logger.addHandler(file_handler)

    return


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{key}={repr(value)}" for key, value in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        arg_names = inspect.signature(func)
        logger.debug(
            f"Method {func.__name__}{arg_names} was called with args ({signature})."
        )
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
            raise e

    return wrapper


def add_logging_to_all(calling_module):
    """
    Applies logging wrapper function to all functions in a module.
    """
    for name, obj in inspect.getmembers(calling_module):
        if inspect.isfunction(obj) and obj.__module__ == calling_module.__name__:
            setattr(obj, "__decorator__", f"{log.__module__}.{log.__name__}")
            calling_module.__dict__[name] = log(obj)
    return


def get_calling_module():
    """Gets the module that calls :py:func:`add_logging_to_all`.

       .. ::note
            All sources online say `inpsect.stack()[1][3]` or
            `inpsect.stack()[1].function` will return the name of the calling
            module. Both these just return the string `"<module>"`. So instead,
            the calling module is found be accessing the local variable attribute
            `f_local` of the FrameInfo object for the calling module, which is
            two up in the stack from this method.


    Returns:
        module: Module calling :py:func:`add_logging_to_all`.
    """
    stack = inspect.stack()
    ## first index of 1 corresponds to the FrameInfo for add_logging_to_all
    locs = getattr(stack[2][0], "f_locals")
    return types.ModuleType(locs['__loader__'].name)
