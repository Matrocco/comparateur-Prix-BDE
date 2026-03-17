import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)

        # Let's try to set the cookies manually before any navigation
        await context.add_cookies([
            {
                "name": "OneyConsent",
                "value": "true",
                "domain": ".auchan.fr",
                "path": "/"
            },
            {
                "name": "journey",
                "value": "%7B%22id%22%3A%22retrait%22%2C%22type%22%3A%22DRIVE%22%2C%22posId%22%3A%22378%22%7D",
                "domain": ".auchan.fr",
                "path": "/"
            }
        ])

        print("Navigation vers l'accueil...")
        await page.goto("https://www.auchan.fr", wait_until="networkidle")

        print("Set localStorage...")
        await page.evaluate("""() => {
            const journey = {
                "journeyId": "retrait",
                "journeyType": "DRIVE",
                "posId": "378", 
                "posName": "Auchan Drive Arras",
                "journeyTypeLabel": "Retrait"
            };
            localStorage.setItem('context', JSON.stringify(journey));
            localStorage.setItem('journey', JSON.stringify(journey));
            
            // Auchan also uses some session storage or other cookies maybe?
            console.log("Cookie: " + document.cookie);
        }""")

        await page.goto("https://www.auchan.fr/recherche?text=lait", wait_until="networkidle")
        
        await page.wait_for_timeout(3000)
        
        try:
            await page.click("button:has-text('Accepter')", timeout=2000)
        except:
            pass
            
        await page.screenshot(path="test_price.png", full_page=True)

        prices = await page.locator("article.product-thumbnail").count()
        print(f"Products: {prices}")
        
        button = await page.locator("button.layerTriggerJourneyReminder").first.inner_text()
        print(f"Header button text: {button}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
