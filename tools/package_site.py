"""Create an uploadable GitHub Pages archive with fewer than 100 files."""

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'artifacts' / 'pages-preview' / 'formus-site'
ARCHIVE = ROOT / 'artifacts' / 'formus-site-upload.zip'


def main():
    # Recreate this generated directory so removed source files cannot survive
    # in an exported site from a previous run.
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sources = [ROOT / name for name in ('index.html', 'contact.html', 'robots.txt', '.nojekyll')]
    sources += [path for directory in ('assets', 'service')
                for path in (ROOT / directory).rglob('*') if path.is_file()]
    paths = []
    for source in sources:
        # A complete font keeps browser uploads below GitHub's 100-file limit.
        if source.name.startswith('noto-sans-jp-') and source.suffix == '.woff2':
            continue
        relative = source.relative_to(ROOT)
        destination = OUTPUT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        paths.append(relative)

    font_css = OUTPUT / 'assets/vendor/fonts/noto-sans-jp.css'
    font_css.write_text('''/* Noto Sans JP 2.004, SIL Open Font License 1.1. */
@font-face {
  font-family: 'Noto Sans JP';
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
  src: url('./files/NotoSansJP-variable.ttf') format('truetype');
}
''')
    font = OUTPUT / 'assets/vendor/fonts/files/NotoSansJP-variable.ttf'
    assert font.is_file(), 'The complete Noto Sans JP font must be present'
    assert len(paths) < 100, 'Too many files for a single GitHub browser upload'
    assert all((OUTPUT / path).stat().st_size < 25 * 1024 * 1024 for path in paths)

    with zipfile.ZipFile(ARCHIVE, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            archive.write(OUTPUT / path, path.as_posix())

    print(json.dumps({'archive': str(ARCHIVE), 'files': len(paths),
                      'archive_bytes': ARCHIVE.stat().st_size,
                      'site_directory': str(OUTPUT)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
