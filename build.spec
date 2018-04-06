# -*- mode: python -*-

block_cipher = None

import sys;
sys.setrecursionlimit(3000)

a = Analysis(['FBP Calculator.pyw'],
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
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='FBP Calculator',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
