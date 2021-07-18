# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['unittest', 'email', 'html', 'http', 'urllib',
            'xml', 'pydoc', 'doctest', 'argparse', 'datetime', 'zipfile',
            'pickle', 'locale', 'calendar', 'gettext', 'tkinter',
            'bz2', 'fnmatch', 'getopt', 'string', 'quopri', 'copy', 'imp',
			'aioflask', 'aiohttp', 'cairo', 'cython', 'flask', 'PIL', 'wand',
			'java.lang', 'xml.parsers', 'datetime', 'java', 'pickle'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += [('icon.ico','icon.ico','DATA'), ('package\Xceed.Wpf.Toolkit.dll','package\Xceed.Wpf.Toolkit.dll','DATA')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='BrawlhallaDisplayPing',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=['vcruntime140.dll', 'ucrtbase.dll'],
          runtime_tmpdir=None,
          console=False , icon='icon.ico')
