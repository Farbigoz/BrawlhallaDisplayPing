from cx_Freeze import setup, Executable

excludes = ['unittest', 'email', 'html', 'http', 'urllib',
            'xml', 'pydoc', 'doctest', 'argparse', 'datetime', 'zipfile',
            'pickle', 'locale', 'calendar',
            'base64', 'gettext',
            'bz2', 'fnmatch', 'getopt', 'string',
            'quopri', 'copy', 'imp']

include_files = ['package', "font.ttf", "config.cfg"]

includes = ['platform', 'encodings.idna']

options = {
    'build_exe': {
        'include_msvcr': True,
        'excludes': excludes,
        'include_files': include_files,
        'includes': includes,
    }
}

setup(
    name = "test",
    version = "0.1",
    description = "Brawlhalla Display Ping",
    executables = [Executable("main.py")],
    options=options
)