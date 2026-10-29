"""Exercise all three static pages and their real animation/form behavior."""

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
PAGES = [('home', '/'), ('service', '/service/'), ('contact', '/contact.html')]
CLEAR_CLIP = re.compile(r'^(?:none|inset\(0(?:px|%)?(?: 0(?:px|%)?){0,3}\))$')


async def main():
    ARTIFACTS.mkdir(exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'),
            headless=True, args=['--no-sandbox'],
        )
        page = await browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors, failed, external, posts, media_requests = [], [], [], [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('response', lambda response: failed.append(response.url) if response.status >= 400 else None)

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

        async def finish_animations():
            await page.evaluate('Promise.all(document.getAnimations().filter(a => a.playState === "running" && a.effect.getComputedTiming().iterations !== Infinity).map(a => a.finished.catch(() => {})))')

        async def visit(path):
            response = await page.goto(BASE + path, wait_until='networkidle')
            assert response.status == 200, path
            assert (await page.title()).startswith('株式会社FORMUS'), path
            await page.evaluate('document.fonts.ready')
            for y in range(0, await page.evaluate('document.body.scrollHeight'), 600):
                await page.evaluate('(y) => scrollTo({top:y,behavior:"instant"})', y)
                await page.wait_for_timeout(70)
            await page.evaluate('scrollTo({top:0,behavior:"instant"})')
            await page.evaluate('Promise.all([...document.images].map(img => img.decode()))')
            await finish_animations()
            assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Horizontal overflow: {path}'
            assert await page.locator('img').evaluate_all('(images) => images.every(img => img.complete && img.naturalWidth > 0)'), f'Broken image: {path}'
            for target in await page.locator('.display-heading, .service-image').all():
                await expect(target).to_have_css('clip-path', CLEAR_CLIP)
            assert await page.locator('.site-header').count() == 1
            assert await page.locator('video, .motion-control, .news-wrap, .news-dialog, .about-image figcaption, .about-principles, .section-topline > span:nth-child(2)').count() == 0
            assert await page.locator('main h1').count() == 1

        async def check_marquee():
            track = page.locator('.marquee-track')
            read_x = '(e) => new DOMMatrix(getComputedStyle(e).transform).m41'
            before = await track.evaluate(read_x)
            scroll_y = await page.evaluate('scrollY')
            await page.wait_for_timeout(300)
            after = await track.evaluate(read_x)
            assert after < before - 8, f'Marquee did not move without scrolling: {before} → {after}'
            assert await page.evaluate('scrollY') == scroll_y
            # Pause at both sides of the actual loop seam and compare the
            # on-screen positions of the matching repeated typography.
            seam = await track.evaluate('''async element => {
                const animation = element.getAnimations()[0];
                const duration = animation.effect.getTiming().duration;
                animation.pause();
                animation.currentTime = duration - .01;
                await new Promise(requestAnimationFrame);
                const before = element.children[1].getBoundingClientRect().left;
                animation.currentTime = duration + .01;
                await new Promise(requestAnimationFrame);
                const after = element.children[0].getBoundingClientRect().left;
                const widths = [...element.children].map(e => e.getBoundingClientRect().width);
                animation.play();
                return {before,after,widths};
            }''')
            assert abs(seam['before'] - seam['after']) < .1, seam
            assert abs(seam['widths'][0] - seam['widths'][1]) < .1, seam
            assert seam['widths'][0] >= page.viewport_size['width'], seam
            # The text band itself is keyboard-operable; no separate visible
            # stop/resume UI is added to the page.
            control = page.locator('.marquee-toggle')
            await control.focus()
            await page.keyboard.press('Enter')
            await expect(control).to_have_attribute('aria-pressed', 'true')
            held = await track.evaluate(read_x)
            await page.wait_for_timeout(180)
            assert abs(await track.evaluate(read_x) - held) < .1
            await page.keyboard.press('Space')
            await expect(control).to_have_attribute('aria-pressed', 'false')
            await page.wait_for_timeout(180)
            assert await track.evaluate(read_x) < held - 4

        for width, height, label in [(1440, 1000, 'desktop'), (390, 844, 'mobile')]:
            await page.set_viewport_size({'width': width, 'height': height})
            for name, path in PAGES:
                await visit(path)
                await page.screenshot(path=str(ARTIFACTS / f'{name}-{label}.png'), full_page=True)
                if name == 'home':
                    await check_marquee()
                if label == 'mobile':
                    menu = page.locator('.menu-toggle')
                    await menu.focus()
                    await page.keyboard.press('Enter')
                    await expect(menu).to_have_attribute('aria-expanded', 'true')
                    await page.keyboard.press('Tab')
                    await expect(page.locator('#main-nav a').first).to_be_focused()
                    await page.keyboard.press('Escape')
                    await expect(menu).to_have_attribute('aria-expanded', 'false')
                    await menu.click()
                    await page.locator('#main-nav a').first.click()
                    await page.wait_for_url(re.compile(r'/(?:index\.html)?#about_blk$'))
                    await expect(page.locator('.menu-toggle')).to_have_attribute('aria-expanded', 'false')

        await page.set_viewport_size({'width': 1440, 'height': 1000})
        await visit('/')
        assert await page.locator('.hero-symbol path').count() == 2
        assert await page.locator('.brand-piece').count() == 2
        assert await page.locator('.about-text p').count() == 5
        assert 'Leading change.' in await page.locator('.hero-en').inner_text()
        # The background mark remains unchanged when the mouse moves.
        logo = page.locator('.hero-symbol')
        before = await logo.evaluate('(e) => getComputedStyle(e).transform')
        await page.mouse.move(300, 400)
        await page.wait_for_timeout(150)
        await page.mouse.move(1000, 700)
        await page.wait_for_timeout(150)
        assert await logo.evaluate('(e) => getComputedStyle(e).transform') == before
        await page.locator('.brand').hover()
        assert await page.locator('.brand-piece').first.evaluate('(e) => e.getAnimations().length > 0')
        company_logo = page.locator('.company-piece').first
        before = await company_logo.evaluate('(e) => getComputedStyle(e).transform')
        await page.locator('.company').scroll_into_view_if_needed()
        await page.wait_for_timeout(200)
        assert await company_logo.evaluate('(e) => getComputedStyle(e).transform') != before
        await page.goto(BASE + '/', wait_until='networkidle')
        service = page.locator('.service-row').first
        await expect(service).to_have_css('opacity', '0')
        await service.scroll_into_view_if_needed()
        await expect(service).to_have_css('opacity', '1')
        await expect(page.locator('.site-header')).to_have_class(re.compile(r'.*\bis-scrolled\b.*'))
        assert await page.locator('.service-row').count() == 2
        await page.locator('.service-row').nth(1).locator('.text-link').click()
        await page.wait_for_url('**/service/#section2')
        await expect(page.locator('#section2 .service-detail-copy')).to_have_css('opacity', '1')
        await page.locator('#section2 .text-link').click()
        await page.wait_for_url('**/contact.html')

        for width, height in [(1440, 1000), (390, 844)]:
            await page.set_viewport_size({'width': width, 'height': height})
            await visit('/contact.html')
            link = page.locator('.policy-link')
            await link.click()
            dialog = page.locator('#privacy')
            await expect(dialog).to_be_visible()
            assert await dialog.locator('h3').count() == 10
            await page.keyboard.press('Escape')
            await expect(dialog).not_to_be_visible()
            await expect(link).to_be_focused()
            await link.click()
            await dialog.locator('.dialog-close').click()
            await expect(dialog).not_to_be_visible()

        form = page.locator('#contact-form')
        await form.locator('button[type="submit"]').click()
        assert await form.evaluate('(form) => !form.checkValidity()')
        assert await page.locator('#form-status').inner_text() == ''
        await form.locator('select').nth(0).select_option('事業内容について')
        await form.locator('select').nth(1).select_option('メール')
        for field, value in {
            '会社名': 'テスト株式会社', 'お名前': 'テスト 太郎', 'フリガナ': 'テスト タロウ',
            'email': 'test@example.com', '電話番号': '03-0000-0000',
            'お問い合わせ内容': '表示・入力の動作確認です。',
        }.items():
            await form.locator(f'[name="{field}"]').fill(value)
        await form.locator('[name="email"]').fill('invalid-address')
        assert not await form.evaluate('(form) => form.checkValidity()')
        await form.locator('[name="email"]').fill('test@example.com')
        assert not await form.evaluate('(form) => form.checkValidity()'), 'Consent must be required'
        await form.locator('input[type="checkbox"]').check()
        await form.locator('button[type="submit"]').click()
        assert '送信されていません' in await page.locator('#form-status').inner_text()
        assert await form.evaluate('(form) => form.checkValidity()')

        # Check narrow phones, tablets and wide monitors, including seamless
        # coverage of the continuous text band on an ultrawide viewport.
        for width in [320, 768, 1024, 2560]:
            await page.set_viewport_size({'width': width, 'height': 1000})
            for _, path in PAGES:
                await visit(path)
            await visit('/')
            await check_marquee()
        await page.emulate_media(reduced_motion='reduce')
        for _, path in PAGES:
            await visit(path)
            assert await page.evaluate('document.getAnimations().length') == 0
            assert await page.locator('video').count() == 0
        await page.goto(BASE + '/', wait_until='networkidle')
        await page.emulate_media(reduced_motion='no-preference')
        await page.wait_for_function('document.querySelector(".marquee-track").getAnimations().length > 0')

        no_js = await browser.new_page(java_script_enabled=False)
        for _, path in PAGES:
            await no_js.goto(BASE + path, wait_until='networkidle')
            target = no_js.locator('.service-row, .service-detail-copy, .contact-form-panel').first
            await expect(target).to_have_css('opacity', '1')
        await expect(no_js.locator('.form-submit')).to_be_disabled()
        await expect(no_js.locator('#privacy')).to_be_visible()
        await no_js.close()
        assert not errors, f'JavaScript errors: {errors}'
        assert not failed, f'HTTP errors: {failed}'
        assert not external, f'External requests: {external}'
        assert not posts, f'Unexpected form delivery: {posts}'
        assert not media_requests, f'Unexpected video downloads: {media_requests}'
        result = {
            'status': 'passed', 'pages': 3, 'viewports': [320, 390, 768, 1024, 1440, 2560],
            'design': 'shared navigation, typography, colors and footer on all three pages',
            'removed': 'NEWS, separate motion control, right-hand section labels, photo captions and split About paragraphs',
            'motion': 'continuous marquee moves without scrolling, loops seamlessly and supports keyboard pause; hero logo ignores mouse; reduced motion and no-JS content passed',
            'services': 'two original descriptions; detail anchors and contact links passed',
            'menu': 'keyboard, focus, navigation and Escape passed on all pages',
            'privacy_modal': 'all ten articles preserved; open, close button, Escape and focus return passed',
            'form': 'required fields, email and consent validated; valid input confirmed locally',
            'javascript_errors': errors, 'failed_requests': failed,
            'external_requests': external, 'outbound_submissions': posts,
        }
        (ARTIFACTS / 'checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
