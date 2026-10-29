"""Export preview and public Xserver packages without changing GitHub's demo."""

import contextlib
import io
import json
import re
import shutil
import zipfile
from pathlib import Path

import package_site

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / 'downloads'


def archive_site(directory, target, relative_paths=None):
    # Stable timestamps make an unchanged package byte-for-byte reproducible.
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        sources = (directory / path for path in relative_paths) if relative_paths is not None else directory.rglob('*')
        for source in sorted(sources):
            if source.is_file():
                info = zipfile.ZipInfo(source.relative_to(directory).as_posix(), (2024, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, source.read_bytes())


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        package_site.main()
    DOWNLOADS.mkdir(exist_ok=True)
    outputs = []
    for mode in ('preview', 'public'):
        destination = ROOT / 'artifacts' / 'xserver' / mode
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(package_site.OUTPUT, destination)
        (destination / '.nojekyll').unlink(missing_ok=True)
        # The preview's JavaScript remains a demo. Only exported Xserver files
        # are connected to the PHP endpoint and the fixed FORMUS mailbox.
        shutil.copy2(ROOT / 'deploy/xserver/contact-submit.php', destination / 'contact-submit.php')
        shutil.copy2(ROOT / 'deploy/xserver/contact-live.js', destination / 'assets/js/contact-live.js')
        (destination / 'assets/js/contact.js').unlink()
        contact = (destination / 'contact.html').read_text()
        contact = contact.replace("form-action 'none'", "form-action 'self'")
        contact = contact.replace('assets/js/contact.js?v=5', 'assets/js/contact-live.js?v=xserver-1')
        contact = contact.replace('<form id="contact-form"', '<form action="contact-submit.php" method="post" id="contact-form"')
        contact = contact.replace(' aria-describedby="form-notice"', '')
        contact = contact.replace('<p id="form-notice" class="form-notice">このページはデザイン確認用です。入力内容は送信されません。</p>', '')
        contact = contact.replace('<span>入力内容を確認する</span>', '<span>お問い合わせを送信する</span>')
        contact = contact.replace('入力確認にはJavaScriptが必要です。個人情報の取り扱いはページ下部でご確認いただけます。', 'フォームの送信にはJavaScriptを有効にしてください。メールでもinfo@formus.jpにご連絡いただけます。個人情報の取り扱いはページ下部でご確認いただけます。')
        contact = contact.replace('<p id="form-status"', '<input type="text" name="website" tabindex="-1" autocomplete="off" hidden aria-hidden="true">\n        <p id="form-status"')
        for field, limit in [(3, 200), (4, 100), (5, 100), (6, 254), (7, 50)]:
            contact = re.sub(rf'(<input id="contact-field-{field}"[^>]+)(>)', rf'\1 maxlength="{limit}"\2', contact)
        (destination / 'contact.html').write_text(contact)

        if mode == 'public':
            for page, url in [('index.html', 'https://formus.jp/'), ('contact.html', 'https://formus.jp/contact.html'), ('service/index.html', 'https://formus.jp/service/')]:
                path = destination / page
                html = path.read_text().replace('  <meta name="robots" content="noindex,nofollow">\n', '')
                html = html.replace('</head>', f'  <link rel="canonical" href="{url}">\n</head>')
                path.write_text(html)
            (destination / 'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /renewal-preview/\nSitemap: https://formus.jp/sitemap.xml\n')
            (destination / 'sitemap.xml').write_text('''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://formus.jp/</loc></url>
  <url><loc>https://formus.jp/service/</loc></url>
  <url><loc>https://formus.jp/contact.html</loc></url>
</urlset>
''')
        archive = DOWNLOADS / f'formus-xserver-{mode}.zip'
        archive_site(destination, archive)
        update = DOWNLOADS / f'formus-xserver-{mode}-contact-update.zip'
        archive_site(destination, update, ['contact.html'])
        outputs.append({'mode': mode, 'archive': str(archive), 'bytes': archive.stat().st_size, 'contact_update': str(update), 'site_directory': str(destination)})
    print(json.dumps(outputs, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
