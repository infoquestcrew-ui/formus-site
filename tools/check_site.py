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
            assert await page.title() == '株式会社FORMUS', path
            await page.evaluate('document.fonts.ready')
            if await page.locator('.load_fist').count():
                await page.locator('.load_fist').wait_for(state='hidden')
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
        slider = page.locator('.mySwiper')
        before = await slider.evaluate('(element) => element.swiper.translate')
        await page.locator('.swiper-button-next').click()
        await expect(page.locator('.swiper-button-next')).to_have_class(
            re.compile(r'.*\bswiper-button-disabled\b.*')
        )
        assert await slider.evaluate('(element) => element.swiper.translate') < before
        assert await slider.evaluate('(element) => element.swiper.isEnd')
        await page.locator('.swiper-slide').nth(1).locator('.btn a').click()
        await page.wait_for_url('**/service/#section2')
        assert await page.locator('#section2').is_visible()

        for name, path in [('home', '/'), ('service', '/service/'),
                           ('contact', '/contact.html')]:
            await page.set_viewport_size({'width': 390, 'height': 844})
            await visit(path)
            await page.screenshot(path=str(ARTIFACTS / f'{name}-mobile.png'),
                                  full_page=True)
            menu = page.locator('.l-header .menu')
            await menu.focus()
            await page.keyboard.press('Enter')
            assert await menu.get_attribute('aria-expanded') == 'true'
            await page.keyboard.press('Escape')
            assert await menu.get_attribute('aria-expanded') == 'false'
            await menu.click()
            await page.locator('.l-header nav a').first.click()
            await page.wait_for_url('**/index.html#about_blk')
            assert 'open' not in (await page.locator('.l-header .menu')
                                 .get_attribute('class')).split()

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
            'video': 'loaded', 'slider': 'navigated to service detail',
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
