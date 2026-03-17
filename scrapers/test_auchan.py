import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        url = "https://www.auchan.fr/recherche?text=lait"
        print("�� Navigation vers Auchan.fr avec query param pour le retrait...")
        await page.goto("https://www.auchan.fr", wait_until="domcontentloaded", timeout=30000)
        
        # Inject context cookies rather than just localStorage (or both)
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
        
        await page.evaluate("""() => {
            const journey = {
                "journeyId": "retrait",
                "journeyType": "DRIVE",
                "posId": "378", 
                "posName": "Auchan Drive Arras",
                "journeyTypeLabel": "Retrait"
            };
            localStorage.setItem("context", JSON.stringify(journey));
            localStorage.setItem("journey", JSON.stringify(journey));
        }""")
        
        print("Rechargement de la page vers rechereche...")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        # Try to trigger store selection from the UI if the context didnt