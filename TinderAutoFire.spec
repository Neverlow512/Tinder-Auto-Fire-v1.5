# tinder_app.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['tinder-panel.py'],  # Main script to start the application
    pathex=['/Users/auto-fire/Desktop/Actual Tinder v1.5/School Field'],  # Path to your project directory
    binaries=[],
    datas=[
        ('tinder.py', '.'),       # Include tinder.py in the root of the bundle
        ('tinder.html', '.'),
        ('config.json', '.'),
	('srn.py', '.'),
	('tinder_paths.py', '.')       # Include config.json in the root of the bundle
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Tinder Auto-Fire',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set this to False to hide the console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
