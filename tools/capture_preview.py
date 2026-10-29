"""Export the actual browser layout and an optional motion GIF for review."""

import argparse
import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('SITE_BASE_URL', 'http://127.0.0.1:4174').rstrip('/')


async def settle(page):
    await page.evaluate('document.fonts.ready')
    step = max(300, int(page.viewport_size['height'] * .7))
    for y in range(0, await page.evaluate('document.body.scrollHeight'), step):
        await page.evaluate('(y) => scrollTo({top:y,behavior:"instant"})', y)
        await page.wait_for_timeout(70)
    await page.evaluate('Promise.all([...document.images].map(image => image.decode()))')
    await page.evaluate('Promise.all(document.getAnimations().filter(a => a.playState === "running" && a.effect.getComputedTiming().iterations !== Infinity).map(a => a.finished.catch(() => {})))')
    await page.evaluate('scrollTo({top:0,behavior:"instant"})')
    await page.wait_for_timeout(150)
    # Freeze the continuous text band only for a sharp still image.
    await page.evaluate('document.getAnimations().filter(a => a.effect.getComputedTiming().iterations === Infinity).forEach(a => a.pause())')
    # A full-page still shows the completed company mark, rather than its
    # off-screen starting pose. The motion recording uses the live scroll state.
    if await page.locator('.company').count():
        await page.locator('.company').evaluate('''element => {
        for (const [key,value] of Object.entries({
            '--company-piece-gap':'0px', '--company-logo-draw':'0',
            '--company-logo-fill':'.9', '--company-logo-y':'0px',
            '--company-logo-turn':'0deg'
        })) element.style.setProperty(key,value);
        }''')


async def main(with_motion):
    output = ROOT / 'designs'
    output.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'),
            args=['--no-sandbox'],
        )
        page = await browser.new_page()
        for label, width, height in [('desktop', 1440, 1000), ('mobile', 390, 844)]:
            await page.set_viewport_size({'width': width, 'height': height})
            for name, path in [('top', '/'), ('service', '/service/'), ('contact', '/contact.html')]:
                await page.goto(BASE + path, wait_until='networkidle')
                await settle(page)
                await page.screenshot(path=str(output / f'formus-{name}-{label}.jpg'), quality=88, full_page=True)
                if name == 'top' and label == 'desktop':
                    await page.screenshot(path=str(output / 'formus-top-hero.jpg'), quality=90)
                    await page.locator('.about').screenshot(path=str(output / 'formus-about-after.jpg'), quality=92)

        if with_motion:
            await page.set_viewport_size({'width': 1120, 'height': 760})
            await page.goto(BASE + '/', wait_until='networkidle')
            await page.evaluate('document.fonts.ready')
            await page.reload(wait_until='domcontentloaded')
            with tempfile.TemporaryDirectory(prefix='formus-motion-') as folder:
                for frame in range(132):
                    if frame == 39:
                        await page.locator('.brand').hover()
                    if frame in (48, 77, 102):
                        selector = {48: '#about_blk', 77: '#service_blk', 102: '#companysns_blk'}[frame]
                        await page.locator(selector).evaluate('(element) => scrollTo({top:element.offsetTop-115,behavior:"smooth"})')
                    await page.screenshot(path=str(Path(folder) / f'frame-{frame:03d}.png'))
                    await page.wait_for_timeout(65)
                subprocess.run([
                    'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                    '-framerate', '9', '-i', str(Path(folder) / 'frame-%03d.png'),
                    '-filter_complex', '[0:v]split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=3',
                    '-loop', '0', str(output / 'formus-motion-preview.gif'),
                ], check=True)
            # Record the actual continuous marquee at rest: no scrolling or
            # pointer movement is needed to move the typography.
            await page.locator('.tagline-marquee').scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            with tempfile.TemporaryDirectory(prefix='formus-marquee-') as folder:
                for frame in range(60):
                    await page.locator('.tagline-marquee').screenshot(path=str(Path(folder) / f'frame-{frame:03d}.png'))
                    await page.wait_for_timeout(75)
                subprocess.run([
                    'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                    '-framerate', '8', '-i', str(Path(folder) / 'frame-%03d.png'),
                    '-filter_complex', '[0:v]split[a][b];[a]palettegen=max_colors=64[p];[b][p]paletteuse=dither=bayer:bayer_scale=3',
                    '-loop', '0', str(output / 'formus-marquee-preview.gif'),
                ], check=True)
        await browser.close()
    print(json.dumps({'output': str(output), 'motion_gif': with_motion}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--motion', action='store_true', help='Also record browser motion; requires ffmpeg.')
    asyncio.run(main(parser.parse_args().motion))
