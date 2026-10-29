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
        errors, failed, external, posts, media_requests = [], [], [], [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('response', lambda response: failed.append(response.url)
                if response.status >= 400 else None)

        async def intercept(route):
            request = route.request
            if request.resource_type == 'media' or urlsplit(request.url).path.endswith(('.mp4', '.webm', '.mov')):
                media_requests.append(request.url)
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
            if await page.locator('.hero').count():
                await page.evaluate('Promise.all(document.getAnimations().filter(a => a.playState === "running").map(a => a.finished.catch(() => {})))')
                for target in await page.locator('.display-heading, .service-image').all():
                    await expect(target).to_have_css(
                        'clip-path', re.compile(r'^(?:none|inset\(0(?:px|%)?(?: 0(?:px|%)?){0,3}\))$')
                    )
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
        assert await page.locator('video, .video-toggle').count() == 0
        assert await page.locator('.hero-symbol path').count() == 2
        assert 'Leading change.' in await page.locator('.hero-en').inner_text()
        await page.goto(BASE + '/', wait_until='networkidle')
        service = page.locator('.service-row').first
        await expect(service).to_have_css('opacity', '0')
        await service.scroll_into_view_if_needed()
        await expect(service).to_have_css('opacity', '1')
        await expect(page.locator('.site-header')).to_have_class(re.compile(r'.*\bis-scrolled\b.*'))
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
        await page.emulate_media(reduced_motion='reduce')
        await page.goto(BASE + '/', wait_until='networkidle')
        await expect(page.locator('.service-row').first).to_have_css('opacity', '1')
        assert await page.evaluate('document.getAnimations().length') == 0
        assert await page.locator('video').count() == 0
        no_js = await browser.new_page(java_script_enabled=False)
        await no_js.goto(BASE + '/', wait_until='networkidle')
        await expect(no_js.locator('.service-row').first).to_have_css('opacity', '1')
        await no_js.close()
        assert not errors, f'JavaScript errors: {errors}'
        assert not failed, f'HTTP errors: {failed}'
        assert not external, f'External requests: {external}'
        assert not posts, f'Unexpected form delivery: {posts}'
        assert not media_requests, f'Unexpected video downloads: {media_requests}'

        result = {
            'status': 'passed', 'pages': 3, 'viewports': [1440, 390],
            'video': 'removed; no video elements or media requests',
            'motion': 'title masks, scroll reveal and floating header passed; reduced motion and no-JS content remain visible',
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
