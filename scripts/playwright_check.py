import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto("https://example.com")
        print("Chromium OK, title:", await page.title())
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
