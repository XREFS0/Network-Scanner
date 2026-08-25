class NetworkScannerError(Exception):
    pass


class InvalidTargetError(NetworkScannerError):
    pass


class InterfaceDetectionError(NetworkScannerError):
    pass


class ScanExecutionError(NetworkScannerError):
    pass


class DatabaseError(NetworkScannerError):
    pass


class ExportError(NetworkScannerError):
    pass
