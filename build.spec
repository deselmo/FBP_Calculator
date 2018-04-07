# -*- mode: python -*-

block_cipher = None

import sys

sys.setrecursionlimit(3000)

filename = 'FBP Calculator'
icon = 'fbp-logo.ico'

binaries = []

if sys.platform == 'win32':
    import os
    python_path = os.path.dirname(sys.executable)
    binaries.append((python_path +
        '\\Lib\\site-packages\\PyQt5\\Qt\\plugins\\styles\\qwindowsvistastyle.dll',
        'PyQt5\\Qt\\plugins\\styles'))

a = Analysis([filename+'.pyw'],
             pathex=[],
             binaries=binaries,
             datas=[],
			 hiddenimports=['six', 'appdirs', 'packaging', 'packaging.version', 'packaging.specifiers', 'packaging.requirements'],
			 hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=filename,
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          icon=icon,
          console=False)

app = BUNDLE(exe,
         name=filename+'.app',
         icon=icon,
         bundle_identifier=None)
