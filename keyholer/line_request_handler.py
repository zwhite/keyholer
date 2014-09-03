from SocketServer import StreamRequestHandler
from traceback import print_exc


class LineRequestHandler(StreamRequestHandler):
    """A server that reads a line and processes it as a single command.

    If the first word of the line matches a cmd_<name> function, that function
    will be called with the remaining words passed in as positional arguments.

    If the first word does not have a corresponding cmd_<name> function we
    return "None".

    Any uncaught exception will result in "Exception" being returned to the
    client.

    This object should not be used directly, but instead should be subclassed.
    """
    def handle(self):
        cmd = self.rfile.readline().strip().split()
        print "client wrote:", cmd

        if hasattr(self, 'cmd_' + cmd[0]):
            try:
                result = getattr(self, 'cmd_' + cmd[0])(*cmd[1:])
                self.write(result)

            except Exception:
                print_exc()
                self.write('Exception')

        else:
            self.write('None')

    def write(self, data):
        return self.wfile.write(data)
