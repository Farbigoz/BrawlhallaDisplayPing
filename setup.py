from cx_Freeze import setup, Executable

excludes = ['unittest', 'email', 'html', 'http', 'urllib',
            'xml', 'pydoc', 'doctest', 'argparse', 'datetime', 'zipfile',
            'pickle', 'locale', 'calendar',
            'base64', 'gettext',
            'bz2', 'fnmatch', 'getopt', 'string',
            'quopri', 'copy', 'imp']

include_files = ['package']

includes = ['platform', 'encodings.idna', 'typing']

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
    executables = [Executable("main.py", targetName="BrawlhallaDisplayPing.exe", icon="icon.ico")],
    options=options
)