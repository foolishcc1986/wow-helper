
class WowKeeperError(Exception):
    pass


class WowKeeperValueError(Exception):
    pass


class ShootError(WowKeeperError):
    pass


class OcrError(WowKeeperError):
    pass


class WowNotRunError(WowKeeperError):
    pass
