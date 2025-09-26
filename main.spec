import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(['src/smol_paste/smol_paste.py'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='smol-paste',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='assets/icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='smol-paste')

app = BUNDLE(coll,
             name='SmolPaste.app',
             icon='assets/icon.icns',
             bundle_identifier='com.github.namuan.smolpaste',
             info_plist={
                'CFBundleName': 'Smol Paste',
                'CFBundleDisplayName': 'Smol Paste',
                'CFBundleVersion': '1.0.0',
                'CFBundleShortVersionString': '1.0.0',
                'CFBundleIdentifier': 'com.github.namuan.smolpaste',
                'NSPrincipalClass': 'NSApplication',
                'NSHighResolutionCapable': True,
                'LSMinimumSystemVersion': '10.13.0',
                'NSRequiresAquaSystemAppearance': False,
                }
             )
