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

        # Étape 1 : aller sur la page d'un magasin Drive pour débloquer les prix
        print("🏪 Sélection du magasin Auchan Drive...")
        await page.goto(
            "https://www.auchan.fr/magasins/drive/arras/er-378",
            wait_until="domcontentloaded",
            timeout=30000
        )

        # Accepter les cookies si la popup apparaît
        try:
            await page.click("button:has-text('Accepter et fermer')", timeout=5000)
            print("✅ Cookies acceptés")
        except:
            pass

        # Choisir le magasin pour activer les prix
        try:
            await page.click("button:has-text('Choisir ce magasin')", timeout=5000)
            await page.wait_for_timeout(2000)
            print("✅ Magasin sélectionné")
        except:
            try:
                await page.click("button:has-text('Faire mes courses')", timeout=5000)
                await page.wait_for_timeout(2000)
                print("✅ Magasin sélectionné (fallback)")
            except:
                print("⚠️ Bouton magasin non trouvé, on continue quand même")

        # Étape 2 : recherche du produit
        print(f"🔍 Recherche de : {produit}")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Scroll pour déclencher le chargement des produits
        await page.evaluate("window.scrollBy(0, 800)")
        await page.wait_for_timeout(2000)

        # Attendre le premier article
        await page.wait_for_selector('article.product-thumbnail', timeout=15000)

        # Récupérer le nom du produit
        nom = await page.evaluate('''() => {
            const selectors = [
                'article.product-thumbnail p[itemprop="name"]',
                'article.product-thumbnail .product-thumbnail__description',
                'article.product-thumbnail p'
            ];
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el && el.innerText.trim()) return el.innerText.trim();
            }
            return "Non trouvé";
        }''')

        # Récupérer le prix — via meta itemprop en priorité (valeur propre sans "€")
        prix_raw = await page.evaluate('''() => {
            // Méthode 1 : balise meta itemprop="price" (la plus fiable)
            const meta = document.querySelector('article.product-thumbnail meta[itemprop="price"]');
            if (meta) return meta.getAttribute('content');

            // Méthode 2 : chercher un élément avec "price" dans la classe qui contient un chiffre
            const els = document.querySelectorAll('article.product-thumbnail [class*="price"]');
            for (const el of els) {
                const t = el.innerText.trim();
                if (t && t !== "Afficher le prix" && /[0-9]/.test(t)) return t;
            }
            return "N/A";
        }''')

        print(f"📦 Nom    : {nom[:80]}")
        print(f"💰 Prix   : {prix_raw}")

        # Nettoyage du prix
        if prix_raw and prix_raw != "N/A":
            prix_final = prix_raw.strip().replace(' ', '').replace('.', ',')
            if '€' not in prix_final:
                prix_final += '€'
        else:
            prix_final = "N/A"

        return {
            "enseigne": "Auchan",
            "nom": nom,
            "prix": prix_final,
            "url": url
        }

    except Exception as e:
        print(f"❌ Erreur Auchan ({produit}): {e}")
        try:
            await page.screenshot(path="/app/debug_auchan_error.png")
            print("📸 Screenshot erreur : /app/debug_auchan_error.png")
        except:
            pass
        return {"enseigne": "Auchan", "nom": "Non trouvé", "prix": "N/A", "url": url}