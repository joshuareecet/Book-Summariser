"""
Written by deanmalmgren for textract
<https://github.com/deanmalmgren/textract/tree/master>
"""

import os

#Filename format
_FILENAME_SUFFIX = '_parser'

EXTENSION_SYNONYMS = {
    ".jpeg": ".jpg",
    ".tff": ".tiff",
    ".tif": ".tiff",
    ".htm": ".html",
    "": ".txt",
    ".log": ".txt",
    ".tab": ".tsv",
}

# traceback from exceptions that inherit from this class are suppressed
class CommandLineError(Exception):
    """The traceback of all CommandLineError's is supressed when the
    errors occur on the command line to provide a useful command line
    interface.
    """
    def render(self, msg):
        return msg % vars(self)

def _get_available_extensions():
    """Get a list of available file extensions to make it easy for
    tab-completion and exception handling.
    """
    extensions = []

    # from filenames
    parsers_dir = os.path.join(os.path.dirname(__file__))
    glob_filename = os.path.join(parsers_dir, "*" + _FILENAME_SUFFIX + ".py")
    # escape backslashes for python 3.6+
    glob_filename = glob_filename.replace("//", "////")
    ext_re = re.compile(glob_filename.replace('*', r"(?P<ext>\w+)"))
    for filename in glob.glob(glob_filename):
        ext_match = ext_re.match(filename)
        ext = ext_match.groups()[0]
        extensions.append(ext)
        extensions.append('.' + ext)

    # from relevant synonyms (don't use the '' synonym)
    for ext in EXTENSION_SYNONYMS.keys():
        if ext:
            extensions.append(ext)
            extensions.append(ext.replace('.', '', 1))
    extensions.sort()
    return extensions

class ExtensionNotSupported(CommandLineError):
    """This error is raised with unsupported extensions"""
    def __init__(self, ext):
        self.ext = ext

        available_extensions = []
        for e in _get_available_extensions():
            if e.startswith('.'):
                available_extensions.append(e)
        self.available_extensions_str = ', '.join(available_extensions)

    def __str__(self):
        return self.render((
            'The filename extension %(ext)s is not yet supported by\n'
            'textract. Please suggest this filename extension here:\n\n'
            '    https://github.com/deanmalmgren/textract/issues\n\n'
            'Available extensions include: %(available_extensions_str)s\n'
        ))


class MissingFileError(CommandLineError):
    """This error is raised when the file can not be located at the
    specified path.
    """
    def __init__(self, filename):
        self.filename = filename
        self.root, self.ext = os.path.splitext(filename)

    def __str__(self):
        return self.render((
            'The file "%(filename)s" can not be found.\n'
            'Is this the right path/to/file/you/want/to/extract%(ext)s?'
        ))


class UnknownMethod(CommandLineError):
    """This error is raised when the specified --method on the command
    line is unknown.
    """
    def __init__(self, method):
        self.method = method

    def __str__(self):
        return self.render((
            'The method "%(method)s" can not be found for this filetype.'
        ))


class ShellError(CommandLineError):
    """This error is raised when a shell.run returns a non-zero exit code
    (meaning the command failed).
    """
    def __init__(self, command, exit_code, stdout, stderr):
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.executable = self.command.split()[0]

    def is_not_installed(self):
        return os.name == 'posix' and self.exit_code == 127

    def not_installed_message(self):
        return (
            "The command `%(command)s` failed because the executable\n"
            "`%(executable)s` is not installed on your system. Please make\n"
            "sure the appropriate dependencies are installed before using\n"
            "textract:\n\n"
            "    http://textract.readthedocs.org/en/latest/installation.html\n"
        ) % vars(self)

    def failed_message(self):
        return (
            "The command `%(command)s` failed with exit code %(exit_code)d\n"
            "------------- stdout -------------\n"
            "%(stdout)s"
            "------------- stderr -------------\n"
            "%(stderr)s"
        ) % vars(self)

    def __str__(self):
        if self.is_not_installed():
            return self.not_installed_message()
        else:
            return self.failed_message()