# characterbuilder.spec
block_cipher = None

# List all your data files
data_files = [
    ('agecategories.csv', '.'),
    ('attrbonuses.csv', '.'),
    ('attributemax.csv', '.'),
    ('attributemins.csv', '.'),
    ('attributevalues.csv', '.'),
    ('excstr.csv', '.'),
    ('levelvalues.csv', '.'),
    ('xpvalues.csv', '.')
]

a = Analysis(
    ['agevalues.py',
     'characterinterface.py',
     'generatecharacter.py',
     'savegamestat.py',
     'datalocus.py',
     'character.py',
     'selectclass.py',
     'attributes.py',
     'hitpoints.py',
     'heightweight.py'],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        'numpy',
        'matplotlib',
        'csv',
        'datetime',
        'functools',
        'operator',
        'pickle',
        'random',
        're',
        'time',
        'typing'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CharacterBuilder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='character.ico'
)