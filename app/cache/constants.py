class Status:
    NOT_FOUND = 'Cache Miss'
    FOUND = 'Cache Hit'

    MAP = {
        True: FOUND,
        False: NOT_FOUND,
    }
