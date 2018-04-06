# -*- mode: python -*-

block_cipher = None

import sys;
sys.setrecursionlimit(3000)
filename = 'FBP Calculator'
a = Analysis([filename+'.pyw'],
             pathex=[],
             binaries=[],
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
icon = 'fbp-logo.ico'
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
          console=False )
app = BUNDLE(exe,
         name=filename+'.app',
         icon=icon,
         bundle_identifier=None)
