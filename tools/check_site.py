"""Exercise the static site in Chromium without allowing external requests."""

import asyncio
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('SITE_BASE_URL', 'http://127.0.0.1:4174').rstrip('/')
ARTIFACTS = ROOT / 'artifacts'


async def main():
    ARTIFACTS.mkdir(exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'),
            headless=True,
            args=['--no-sandbox'],
        )
        page = await browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors, failed, external, posts = [], [], [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('response', lambda response: failed.append(response.url)
                if response.status >= 400 else None)

        async def intercept(route):
            request = route.request
            if request.method != 'GET':
                posts.append(request.url)
                await route.abort()
            elif urlsplit(request.url).netloc != urlsplit(BASE).netloc:
                external.append(request.url)
                await route.abort()
            else:
                await route.continue_()

        await page.route('**/*', intercept)

        async def visit(path):
            response = await page.goto(BASE + path, wait_until='networkidle')
            assert response.status == 200, path
            assert (await page.title()).startswith('株式会社FORMUS'), path
            await page.evaluate('document.fonts.ready')
            if await page.locator('.load_fist').count():
                await page.locator('.load_fist').wait_for(state='hidden')
            # Load every lazy image before checking/capturing the entire page.
            for y in range(0, await page.evaluate('document.body.scrollHeight'), 700):
                await page.evaluate('(y) => window.scrollTo({top: y, behavior: "instant"})', y)
                await page.wait_for_timeout(60)
            await page.evaluate('window.scrollTo({top: 0, behavior: "instant"})')
            await page.evaluate('Promise.all([...document.images].map(img => img.decode()))')
            assert await page.evaluate(
                'document.documentElement.scrollWidth <= innerWidth'
            ), f'Horizontal overflow: {path}'
            assert await page.locator('img').evaluate_all(
                '(images) => images.every(img => img.complete && img.naturalWidth > 0)'
            ), f'Broken image: {path}'

        for name, path in [('home', '/'), ('service', '/service/'),
                           ('contact', '/contact.html')]:
            await visit(path)
            await page.screenshot(path=str(ARTIFACTS / f'{name}-desktop.png'),
                                  full_page=True)

        await visit('/')
        video = page.locator('video')
        await expect(video).to_have_js_property('readyState', 4)
        assert await video.evaluate('(video) => video.videoWidth > 0')
        assert await video.evaluate('(video) => video.muted && video.loop')
        await page.locator('.video-toggle').click()
        await expect(video).to_have_js_property('paused', True)
        await page.locator('.video-toggle').click()
        await expect(video).to_have_js_property('paused', False)
        await page.locator('[data-news-open]').click()
        await expect(page.locator('.news-dialog')).to_be_visible()
        await page.keyboard.press('Escape')
        await expect(page.locator('.news-dialog')).not_to_be_visible()
        assert await page.locator('.service-row').count() == 2
        await page.locator('.service-row').nth(1).locator('.text-link').click()
        await page.wait_for_url('**/service/#section2')
        assert await page.locator('#section2').is_visible()

        for name, path in [('home', '/'), ('service', '/service/'),
                           ('contact', '/contact.html')]:
            await page.set_viewport_size({'width': 390, 'height': 844})
            await visit(path)
            await page.screenshot(path=str(ARTIFACTS / f'{name}-mobile.png'),
                                  full_page=True)
            home = await page.locator('.menu-toggle').count() > 0
            menu = page.locator('.menu-toggle' if home else '.l-header .menu')
            await menu.focus()
            await page.keyboard.press('Enter')
            await expect(menu).to_have_attribute('aria-expanded', 'true')
            if home:
                await page.keyboard.press('Tab')
                await expect(page.locator('#main-nav a').first).to_be_focused()
            await page.keyboard.press('Escape')
            await expect(menu).to_have_attribute('aria-expanded', 'false')
            await menu.click()
            await page.locator('#main-nav a' if home else '.l-header nav a').first.click()
            await page.wait_for_url(re.compile(r'/(?:index\.html)?#about_blk$'))
            await expect(page.locator('.menu-toggle')).to_have_attribute('aria-expanded', 'false')

        await visit('/contact.html')
        await page.locator('a.policy-link').click()
        await page.locator('.modaal-wrapper').wait_for(state='visible')
        assert await page.locator('.modaal-wrapper').inner_text()
        await page.keyboard.press('Escape')
        await page.locator('.modaal-wrapper').wait_for(state='detached')

        form = page.locator('#contact-form')
        await form.locator('button[type="submit"]').click()
        assert await form.evaluate('(form) => !form.checkValidity()')
        assert await page.locator('#form-status').inner_text() == ''
        await form.locator('select').nth(0).select_option('事業内容について')
        await form.locator('select').nth(1).select_option('メール')
        for field, value in {
            '会社名': 'テスト株式会社', 'お名前': 'テスト 太郎',
            'フリガナ': 'テスト タロウ', 'email': 'test@example.com',
            '電話番号': '03-0000-0000', 'お問い合わせ内容': '表示・入力の動作確認です。',
        }.items():
            await form.locator(f'[name="{field}"]').fill(value)
        await form.locator('input[type="checkbox"]').check()
        await form.locator('button[type="submit"]').click()
        assert '送信されていません' in await page.locator('#form-status').inner_text()
        assert await form.evaluate('(form) => form.checkValidity()')
        assert not errors, f'JavaScript errors: {errors}'
        assert not failed, f'HTTP errors: {failed}'
        assert not external, f'External requests: {external}'
        assert not posts, f'Unexpected form delivery: {posts}'

        result = {
            'status': 'passed', 'pages': 3, 'viewports': [1440, 390],
            'video': 'loaded, paused and resumed',
            'services': 'two service introductions; detail link navigated',
            'news': 'dialog opened and closed with Escape',
            'menu': 'pointer, keyboard, navigation, Escape passed',
            'privacy_modal': 'open and Escape close passed',
            'form': 'invalid blocked; valid input confirmed locally',
            'javascript_errors': errors, 'failed_requests': failed,
            'external_requests': external, 'outbound_submissions': posts,
        }
        (ARTIFACTS / 'checks.json').write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
