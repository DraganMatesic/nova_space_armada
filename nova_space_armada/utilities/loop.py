from time import sleep
from datetime import datetime
from nova_space_armada.utilities.log import log


def execute_method(method, cls: object, timeout: int = None, iterations: int = None, raise_flag: bool = False, wait: int= 1):
    """
    :param cls:
    :param method:
    :param timeout:
    :param iterations:
    :param raise_flag:
    :return:
    """
    start_time = datetime.now()
    cnt = 0
    while True:

        # check if iterations param is provided
        if iterations is not None:
            cnt += 1
            if cnt > iterations:
                message = f"max number of iterations ({iterations}) reached for class method {method.__name__}"
                if raise_flag is True:
                    raise StopIteration(message)
                else:
                    log(message)
                    break

        # check if timeout param is provided
        if timeout is not None:
            if abs((start_time - datetime.now()).total_seconds()) > timeout:
                message = f"loop timeout during executing class method {method.__name__}"
                if raise_flag is True:
                    raise TimeoutError(message)
                else:
                    log(message)
                    break

        if type(method) is str:
            result = getattr(cls, method)()
        else:
            result = method()

        # if method class returned True loop can be closed
        if result is True:
            break
        sleep(wait)



