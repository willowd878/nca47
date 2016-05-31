import paramiko
import re
import socket
from oslo_log import log as logging
from oslo_config import cfg
from nca47.common.i18n import _
from nca47.common.i18n import _LE
from nca47.common.i18n import _LW

# py2 vs py3; replace with six via ziploader
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

LOG = logging.getLogger(__name__)

CLI_OS_OPTS = [
    cfg.StrOpt('device_type',
               default='cisco',
               help=_('the target device type which would be connect')),
    cfg.StrOpt('host',
               default='127.0.0.1',
               help=_('The server hostname/ip to connect to.')),
    cfg.IntOpt('port',
               default=22,
               help=_('he server port to connect to')),
    cfg.StrOpt('username',
               default='admin',
               help=_('the username to authenticate on ssh connect.')),
    cfg.StrOpt('password',
               default='password',
               help=_('a password to use for authentication or for '
                      'unlocking a private key')),
    cfg.BoolOpt('authorize',
                default=False,
                help=_('whether need to enable operation privilege')),
    cfg.StrOpt('auth_pass',
               default='auth_pass',
               help=_('the password which authorize operation privilege'))
]

CONF = cfg.CONF
opt_group = cfg.OptGroup(name='cli_backend',
                         title='Options for device ssh connection '
                               'informations')
CONF.register_group(opt_group)
CONF.register_opts(CLI_OS_OPTS, opt_group)

internal_log_path = 'sshClient.log'

AUTH_ERROR_RE = re.compile(r"access denied", re.I),
AUTH_PASSWD_RE = re.compile(r"[\r\n]?password:", re.I)
NEED_AUTH_RE = re.compile(r"permission denied", re.I)

CLI_ERRORS_RE = [
    re.compile(r"% ?Error"),
    re.compile(r"% ?Bad secret"),
    re.compile(r"invalid (?:parameter|command|input)", re.I),
    re.compile(r"incomplete ip prefix", re.I),
    re.compile(r"invalid ip address", re.I),
    re.compile(r"(?:incomplete|ambiguous) command", re.I),
    re.compile(r"connection timed out", re.I),
    re.compile(r"[^\r\n]+ not found", re.I),
    re.compile(r"'[^']' +returned error code: ?\d+"),
    re.compile(r"user doesn't have any privilege", re.I),
]

CLI_PROMPTS_RE = [
    re.compile(r"[\r\n]?[\w+\-\.:\/\[\]]+(?:\([^\)]+\)){,3}(?:>|#) ?$"),
    re.compile(r"\[\w+\@[\w\-\.]+(?: [^\]])\] ?[>#\$] ?$")
]


def to_list(val):
    if isinstance(val, (list, tuple)):
        return list(val)
    elif val is not None:
        return [val]
    else:
        return list()


class ShellError(Exception):

    def __init__(self, msg, command=None):
        super(ShellError, self).__init__(msg)
        self.message = msg
        self.command = command


class AuthError(Exception):

    def __init__(self, msg, command=None):
        super(ShellError, self).__init__(msg)
        self.message = msg
        self.command = command


class Command(object):

    def __init__(self, command, prompt=None, response=None):
        self.command = command
        self.prompt = prompt
        self.response = response

    def __str__(self):
        return self.command


class sshClient():
    """
    Represent an ssh session on target ssh server, call paramiko module
    to generate it
    """

    def __init__(self, agent_type=None, target_host=None, port=22,
                 username=None, password=None, authorize=False,
                 auth_pass=None, prompts_re=None, errors_re=None, **kwargs):

        self.device_type = CONF.cli_backend.device_type
        self.host = target_host or CONF.cli_backend.host
        self.port = port or CONF.cli_backend.port
        self.username = username or CONF.cli_backend.username
        self.password = password or CONF.cli_backend.password
        self.authorize = authorize or CONF.cli_backend.authorize
        self.auth_pass = auth_pass or CONF.cli_backend.auth_pass
        self.prompts = prompts_re or CLI_PROMPTS_RE
        self.errors = errors_re or CLI_ERRORS_RE
        self._client = None
        self._channel = None
        self._logon_info = ''
        self._connected = False
        self.command_result = {}
        self.connect()

    @property
    def connected(self):
        return self._connected

    def connect(self, hostkeys_file=None):
        self._logon_info += 'Loginng Host: %s, Port: %d\n' % (self.host,
                                                              self.port)
        self._logon_info += 'Login User: %s, password: %s\n' % (self.username,
                                                                self.password)
        paramiko.util.log_to_file(internal_log_path)
        self._client = paramiko.SSHClient()
        self._client.load_system_host_keys(hostkeys_file)
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            # Connect to an SSH server and authenticate to it.
            self._client.connect(self.host, self.port, self.username,
                                 self.password)

            self._channel = self._client.invoke_shell()
            if self.authorize:
                self.auth()
            self.disable_paging(self.device_type)
            self._connected = True
            self._logon_info += 'Login Successful!\n'
        except Exception as e:
            LOG.error(_LE("Connect to host %s failed\n" % self.host))
            self._logon_info += e.message
            raise e

    def auth(self):
        res = self.send(Command('enable', prompt=AUTH_PASSWD_RE,
                                response=self.auth_pass))

        auth_res_info = AUTH_PASSWD_RE.findall(res[0])
        if len(auth_res_info) > 1:
            raise ShellError('Authorize failed under authorize password as %s'
                             % self.auth_pass)

    def disable_paging(self, device_type):
        if device_type == 'cisco':
            self.send('terminal length 0')
        elif device_type == 'firewall':
            # to do work-dzyu
            self.send('terminal length 0')
        else:
            LOG.warning(_LW('current not support %s device type disable '
                            'paging function'))

    def send(self, commands):
        responses = list()
        run_result = {}
        try:
            for command in to_list(commands):
                cmd = '%s\r' % str(command)
                self._channel.sendall(cmd)
                cmd_result = self.combine_result(command,
                                                 self.receive(command))
                responses.append(cmd_result)
                run_result[command] = 'SUCCESS'
            self.log_to_file(responses)
        except socket.timeout:
            raise ShellError("timeout trying to send command", cmd)
        return run_result

    def combine_result(self, command, result):
        cmd = str(command)
        prefix = "COMMAND: < %s > result -----> \r" % cmd
        cmd_result = str(result)
        if not cmd_result.strip():
            cmd_result = "---------no returned value---------"
        return prefix + cmd_result

    def receive(self, cmd=None):
        recv = StringIO()
        while True:
            data = self._channel.recv(200)

            recv.write(data)
            recv.seek(recv.tell() - 200)

            window = recv.read()
            if isinstance(cmd, Command):
                self.handle_input(window, prompt=cmd.prompt,
                                  response=cmd.response)
            try:
                if self.read(window):
                    return self.sanitize(cmd, recv.getvalue())
            except ShellError, exc:
                exc.command = cmd
                raise

    def read(self, response):
        if NEED_AUTH_RE.search(response):
            raise ShellError('No authorize to execute command %s' % response)
        for regex in self.errors:
            if regex.search(response):
                raise ShellError('matched error in response: %s' % response)

        for regex in self.prompts:
            match = regex.search(response)
            if match:
                self._matched_prompt = match.group()
                return True

    def sanitize(self, cmd, resp):
        cleaned = []
        for line in resp.splitlines():
            if line.startswith(str(cmd)) or self.read(line):
                continue
            cleaned.append(line)
        return "\n".join(cleaned)

    def configure(self, commands):
        commands = to_list(commands)
        commands.insert(0, 'configure terminal')
        responses = self.execute(commands)
        responses.pop(0)
        return responses

    def handle_input(self, resp, prompt, response):
        if not prompt or not response:
            return
        prompt = to_list(prompt)
        response = to_list(response)

        for pr, ans in zip(prompt, response):
            match = pr.search(resp)
            if match:
                cmd = '%s\r' % ans
                self._channel.sendall(cmd)

    def log_to_file(self, responses, filename='response_result.txt'):
        """
        send response logs to one logfile, if they're not already
        going somewhere
        """
        f = open(filename, 'w')
        for res in responses:
            f.write('%s\n' % res)
        f.close()

    def close(self):
        if self._channel is not None:
            self._channel.close()
        self._client.close()
        self._client = None
        self._channel = None
        self._result = None


if __name__ == '__main__':
    client = sshClient()
    client.connect()

    if client.connected:
        commands_list = ['show run']
        response = client.send(commands_list)
        for res in response:
            print res
    client.close()
