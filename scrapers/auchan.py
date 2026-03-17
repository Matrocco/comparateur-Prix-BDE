from playwright.async_api import Page
from playwright_stealth import Stealth

async def block_useless_resources(route):
    if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
        await route.abort()
    else:
        await route.continue_()

async def scrape_auchan(page: Page, produit: str):
    url = f"https://www.auchan.fr/recherche?text={produit.replace(' ', '%20')}"
    try:
        await Stealth().apply_stealth_async(page)
        await page.route("**/*", block_useless_resources)
        await page.goto("https://www.auchan.fr", wait_until="domcontentloaded", timeout=30000)
        # Navigate to a specific store page to set the context via backend session
        await page.goto("https://www.auchan.fr/magasins/drive/arras/er-378", wait_until="domcontentloaded", timeout=30000)
        
        try:
            await page.click("button:has-text('Accepter et fermer')", timeout=5000)
        except:
            pass
            
        try:
            # S'il y a un bouton pour choisir ce magasin, on clique dessus
            async with page.expect_response(lambda response: True, timeout=10000):
                await page.click("button:has-text('Choisir ce magasin')", timeout=10000)
            await page.wait_for_timeout(3000)
        except:
            try:
                # Fallback JS pour forcer le clic si un overlay bloque
                await page.evaluate('''() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const btn = buttons.find(b => b.innerText.includes('Choisir ce magasin') || b.innerText.includes('Faire mes courses'));
                    if (btn) btn.click();
                }''')
                await page.wait_for_timeout(3000)
            except:
                pass
        
        # Navigate to search now that store context is set
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Screenshot forcé juste après le chargement
        await page.screenshot(path="/app/debug_auchan.png", full_page=False)
        print("📸 Screenshot pris après chargement")

        try:
            await page.click("button:has-text('Accepter et fermer')", timeout=5000)
            print("✅ Cookies acceptés")
            await page.screenshot(path="/app/debug_auchan_after_cookies.png")
        except:
            print("⚠️ Pas de popup cookies")

        # Wait for the new article thumbnail selectors
        await page.wait_for_selector('article.product-thumbnail', timeout=10000)
        
        # Add a short delay to let specific price text render in React
        await page.wait_for_timeout(2000)

        nom = await page.evaluate('''() => {
            let el = document.querySelector('article.product-thumbnail p[itemprop="name description"], article.product-thumbnail .product-thumbnail__description');
            return el ? el.innerText : "Non trouvé";
        }''')
        
        prix_raw = await page.evaluate('''() => {
            let meta = document.querySelector('article.product-thumbnail meta[itemprop="price"]');
            if (meta) return meta.getAttribute('content');
            let priceEl = document.querySelector('article.product-thumbnail .product-price, article.product-thumbnail [class*="price"]');
            if (priceEl) return priceEl.innerText;
            return "N/A";
        }''')
        
        prix_final = prix_raw.strip().replace(' ', '').replace('.', ',') if prix_raw else "N/A"
        if prix_final != "N/A" and '€' not in prix_final:
            prix_final += '€'

        return {
            "enseigne": "Auchan",
            "nom": nom.strip(),
            "prix": prix_final,
            "url": url
        }

    except Exception as e:
        import traceback
        with open("/app/error.log", "w") as f:
            f.write(traceback.format_exc())
        print(f"❌ Erreur Auchan ({produit}): {e}")
        try:
            await page.screenshot(path="/app/debug_auchan_error.png")
            print("📸 Screenshot erreur sauvegardé")
        except Exception as e2:
            print(f"❌ Impossible de prendre screenshot : {e2}")
        return {"enseigne": "Auchan", "nom": "Non trouvé", "prix": "N/A", "url": url}