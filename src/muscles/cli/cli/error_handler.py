

class ConsoleErrorHandler(Exception):

    def handler(self, reason: str = None):
        return Exception(reason)
