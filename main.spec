# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['E:\\Brawlhalla_ping_tester'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['unittest', 'email', 'html', 'http', 'urllib',
            'xml', 'pydoc', 'doctest', 'argparse', 'datetime', 'zipfile',
            'pickle', 'locale', 'calendar',
            'base64', 'gettext',
            'bz2', 'fnmatch', 'getopt', 'string',
            'quopri', 'copy', 'imp'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
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
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='icon.ico')