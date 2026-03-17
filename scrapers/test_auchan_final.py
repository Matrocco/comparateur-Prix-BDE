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
        
        print("Navigate directly to Arras drive...")
        await page.goto("https://www.auchan.fr/magasins/drive/arras/er-378", wait_until="networkidle", timeout=30000)
        
        try:
            await page.click("button:has-text(\"Accepter et fermer\")", timeout=5000)
            print("Cookies acceptés")
        except:
            pass
            
        try:
            print("Click Choisir ce magasin...")
            async with page.expect_response(lambda response: True, timeout=10000): # Wait for *any* response triggered by the click
                await page.click("button:has-text(\"Choisir ce magasin\")", timeout=5000)
            print("Attente de 3 sec pour etre sur...")
            await page.wait_for_timeout(3000)
        except Exception as e:
            print("Pas de bouton Choisir:", e)
            try:
                await page.click("button:has-text(\"Faire mes courses\")", timeout=5000)
                await page.wait_for_timeout(3000)
            except Exception:
                pass
                
        url = "https://www.auchan.fr/recherche?text=lait"
        print("🌍 Navigation vers Auchan.fr recherche...")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        
        await page.wait_for_timeout(3000)
        
        print("Recherche meta price ou span price...")
        try:
            html = await page.locator("article.product-thumbnail").first.inner_html()
            print(html)
        except Exception as e:
            print("Erreur dumping html", e)
            
        prix_raw = await page.evaluate("""() => {
            let meta = document.querySelector("article.product-thumbnail meta[itemprop=\\\"price\\\"]");
            if (meta) return meta.getAttribute("content");
            let priceEl = document.querySelector("article.product-thumbnail .product-price, article.product-thumbnail [class*=\\\"price\\\"]");
            if (priceEl) return priceEl.innerText;
            return "N/A";
        }""")
        print("Prix raw extrait :", prix_raw)
            
        print("Done")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
