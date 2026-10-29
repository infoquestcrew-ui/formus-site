"""Test the Xserver export and PHP mail handler with a local-only mail capture."""

import asyncio
import email
import email.policy
import http.cookiejar
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

from playwright.async_api import async_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
PHP = os.environ.get('PHP_BIN') or shutil.which('php')
FIELDS = {
    'お問い合わせ種別': '事業内容について', 'ご希望の連絡方法': 'メール',
    '会社名': 'テスト株式会社', 'お名前': '確認 太郎', 'フリガナ': 'カクニン タロウ',
    'email': 'visitor@example.com', '電話番号': '03-0000-0000',
    'お問い合わせ内容': '送信の動作確認です。\n' + '日' * 480,
    '個人情報の取り扱い': '同意する', 'website': '',
}


class Client:
    def __init__(self, base):
        self.base = base
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def get_token(self):
        with self.opener.open(self.base + '/contact-submit.php') as response:
            assert response.headers['Cache-Control'].startswith('no-store')
            assert 'HttpOnly' in response.headers.get('Set-Cookie', '')
            assert 'SameSite=Strict' in response.headers.get('Set-Cookie', '')
            return json.load(response)['csrf']

    def post(self, fields, origin=None, method='POST'):
        request = urllib.request.Request(
            self.base + '/contact-submit.php', data=urllib.parse.urlencode(fields).encode(), method=method,
            headers={'Origin': self.base if origin is None else origin},
        )
        try:
            response = self.opener.open(request)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)


async def browser_check(base, runtime, outbox, failure_flag):
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
        page = await browser.new_page(viewport={'width':390,'height':844})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        await page.goto(base + '/contact.html', wait_until='networkidle')
        form = page.locator('#contact-form')
        button = form.locator('[type="submit"]')
        await expect(button).to_be_enabled()
        await button.click()
        assert not await form.evaluate('(f) => f.checkValidity()')
        assert not outbox.exists() or not outbox.read_text().strip()
        await form.locator('select').nth(0).select_option(FIELDS['お問い合わせ種別'])
        await form.locator('select').nth(1).select_option(FIELDS['ご希望の連絡方法'])
        for field in ('会社名','お名前','フリガナ','email','電話番号','お問い合わせ内容'):
            await form.locator(f'[name="{field}"]').fill(FIELDS[field])
        await form.locator('[type="checkbox"]').check()
        failure_flag.touch()
        await button.click()
        await expect(page.locator('#form-status')).to_contain_text('送信できませんでした')
        await expect(button).to_be_enabled()
        await expect(form.locator('[name="会社名"]')).to_have_value(FIELDS['会社名'])
        failure_flag.unlink()
        await button.click()
        await expect(page.locator('#form-status')).to_contain_text('お問い合わせを受け付けました')
        await expect(button).to_be_disabled()
        await expect(form.locator('[name="会社名"]')).to_have_value('')
        assert len(outbox.read_text().splitlines()) == 1
        assert not errors, errors
        await browser.close()


def main():
    if not PHP:
        raise SystemExit('Install PHP 8.3+ or set PHP_BIN to its executable path.')
    subprocess.run(['python3', str(ROOT/'tools/package_xserver.py')], check=True, stdout=subprocess.DEVNULL)
    for mode in ('preview','public'):
        site = ROOT/'artifacts/xserver'/mode
        for page in ('index.html','contact.html','service/index.html'):
            html = (site/page).read_text()
            assert ('noindex,nofollow' in html) == (mode == 'preview')
            assert ('rel="canonical"' in html) == (mode == 'public')
        assert "form-action 'self'" in (site/'contact.html').read_text()
        assert 'デザイン確認用' not in (site/'contact.html').read_text()
        assert not (site/'assets/js/contact.js').exists()
        assert (site/'contact-submit.php').is_file()
        with zipfile.ZipFile(ROOT/f'downloads/formus-xserver-{mode}.zip') as archive:
            assert 'index.html' in archive.namelist()
            assert 'contact-submit.php' in archive.namelist()
            assert not any(name.startswith(('/', '../')) for name in archive.namelist())
            assert '.htaccess' not in archive.namelist(), 'Never overwrite existing server/SSL settings'
    site = ROOT/'artifacts/xserver/public'
    subprocess.run([PHP, '-n', '-l', str(site/'contact-submit.php')], check=True, stdout=subprocess.DEVNULL)
    with tempfile.TemporaryDirectory(prefix='formus-mail-check-') as folder:
        runtime = Path(folder)
        (runtime/'sessions').mkdir()
        (runtime/'tmp').mkdir()
        outbox = runtime/'outbox.jsonl'
        failure_flag = runtime/'fail-mail'
        capture = runtime/'sendmail-capture'
        capture.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
if Path(os.environ['FORMUS_TEST_MAIL_FAILURE']).exists(): sys.exit(75)
with open(os.environ['FORMUS_TEST_MAIL_OUTBOX'],'a') as output:
    output.write(json.dumps({'argv':sys.argv[1:], 'mail':sys.stdin.read()},ensure_ascii=False)+'\\n')
''')
        capture.chmod(0o700)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0))
            port = sock.getsockname()[1]
        base = f'http://127.0.0.1:{port}'
        environment = dict(os.environ, FORMUS_TEST_MAIL_OUTBOX=str(outbox), FORMUS_TEST_MAIL_FAILURE=str(failure_flag))
        with (runtime/'server.log').open('w+') as log:
            server = subprocess.Popen([
                PHP, '-n', '-d', f'sendmail_path={capture} -t -i',
                '-d', f'sys_temp_dir={runtime/"tmp"}', '-d', f'session.save_path={runtime/"sessions"}',
                '-S', f'127.0.0.1:{port}', '-t', str(site),
            ], env=environment, stdout=log, stderr=subprocess.STDOUT)
            try:
                for _ in range(60):
                    try:
                        with urllib.request.urlopen(base + '/contact.html', timeout=1): break
                    except OSError: time.sleep(.1)
                else: raise AssertionError('PHP server did not start')
                client = Client(base)
                token = client.get_token()
                valid = dict(FIELDS, csrf=token)
                assert client.post(FIELDS)[0] == 403
                assert client.post(valid, origin='https://unrelated.example')[0] == 403
                for update in [{'email':'bad-address'}, {'email':'a@example.com\r\nBcc: x@example.com'}, {'個人情報の取り扱い':''}, {'お問い合わせ種別':'not-an-option'}, {'お問い合わせ内容':'日'*501}, {'website':'spam'}]:
                    assert client.post(dict(valid, **update))[0] == 422, update
                arrays = dict(valid)
                arrays.pop('会社名')
                arrays['会社名[]'] = 'invalid array'
                assert client.post(arrays)[0] == 422
                assert not outbox.exists()
                assert client.post(dict(valid, recipient='attacker@example.com'))[0] == 200
                records = [json.loads(line) for line in outbox.read_text().splitlines()]
                assert len(records) == 1
                message = email.message_from_string(records[0]['mail'], policy=email.policy.default)
                assert str(message['To']) == 'info@formus.jp'
                assert str(message['From']) == 'FORMUS <info@formus.jp>'
                assert str(message['Reply-To']) == FIELDS['email']
                assert str(message['Subject']) == '【FORMUS】お問い合わせ'
                assert FIELDS['お問い合わせ内容'] in message.get_content().replace('\r\n','\n')
                assert '-finfo@formus.jp' in records[0]['argv']
                assert client.post(valid)[0] == 403, 'A successful token cannot be reused'
                peer = Client(base)
                assert peer.post(dict(FIELDS, csrf=peer.get_token()))[0] == 429, 'Rate limit must span sessions'
                assert len(outbox.read_text().splitlines()) == 1
                for entry in (runtime/'tmp').glob('formus-contact-*'): shutil.rmtree(entry)
                outbox.unlink()
                asyncio.run(browser_check(base, runtime, outbox, failure_flag))
                # No personal message body or visitor email is written to server logs.
                log.flush()
                log.seek(0)
                assert FIELDS['email'] not in log.read()
            finally:
                server.terminate()
                server.wait(timeout=10)
    print(json.dumps({
        'status':'passed','packages':['preview','public'],
        'mail':'captured locally; fixed info@formus.jp recipient and sender, visitor Reply-To, Japanese body and subject passed',
        'validation':'required fields, email/header injection, consent, allowed choices, Unicode length and array inputs passed',
        'request_controls':'same-origin, session/CSRF, duplicate prevention, honeypot and rate limits across sessions passed',
        'browser':'mobile form blocks invalid input, preserves input on transport failure and accepts one explicit retry',
        'real_emails_sent':0,'xserver_delivery':'requires upload and real receipt check on the user server',
    },ensure_ascii=False,indent=2))


if __name__ == '__main__': main()
