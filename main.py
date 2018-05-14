import click
# Add this to avoid the annoying warning: http://click.pocoo.org/5/python3/
click.disable_unicode_literals_warning = True
import sys
import time
from select import select

# Internal modules
from sockets import SocketServer, ThreadedSocketServer, SocketClient, ThreadedSocketServerCombo

def main():
    @click.group(help="Test sockets")
    @click.pass_context
    def cli(ctx):
        pass

    @cli.command(help="Launch Server")
    def server():
        sock_server = SocketServer()
        sock_server.start()

    @cli.command(help="Launch Threaded Server")
    def threaded_server():
        sock_server = ThreadedSocketServer()
        sock_server.start()

    @cli.command(help="Launch Worker Server")
    def worker_server():
        sock_server = ThreadedSocketServerCombo()
        sock_server.start()

    @cli.command(help="Launch Client")
    @click.argument('cmd_args', nargs=-1)
    def client(cmd_args):
        if cmd_args:
            click.echo("args: {}".format(cmd_args))
        sock_client = SocketClient()
        sock_client.start()
        if cmd_args:
            msg = " ".join(cmd_args)
            print "SENDING:", msg
            sock_client.write(msg)
            print "Shutting down."
            return
        timeout = 5
        click.echo("> ", nl=False)
        while True:
            try:
                # Enable exit triggered by server shutdown at max delay 5s
                rlist, _, _ = select([sys.stdin], [], [], timeout)
                if rlist:
                    s = sys.stdin.readline().strip()
                    if not s:
                        click.echo("> ", nl=False)
                        continue
                    print "SENDING:", s
                    sock_client.write(s)
                    if "DONE" == s:
                        break
                    click.echo("> ", nl=False)
            except KeyboardInterrupt:
                print "Shutting down."
                sock_client.close()
                break
        else:
            print "Couldn't Connect!"
        print "Done"

    cli(obj={}, standalone_mode=False)

try:
    main()
except click.exceptions.Abort:
    print 'Aborted'
