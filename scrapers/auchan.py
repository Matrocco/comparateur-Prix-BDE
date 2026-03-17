# scrapers/auchan.py

async def scrape_auchan(page, produit):
    try:
        # On utilise la page passée depuis app.py, pas de nouveau browser
        await page.goto(
            f"https://www.auchan.fr/recherche?text={produit}",
            timeout=60000,  # 60s au lieu de 30s
            wait_until="domcontentloaded"  # n'attend pas le JS complet
        )

        # Attendre qu'un produit apparaisse
        await page.wait_for_selector(".product-card", timeout=15000)

        # Récupérer le premier résultat
        nom = await page.locator(".product-card__name").first.inner_text()
        prix = await page.locator(".product-card__price").first.inner_text()
        url = await page.locator(".product-card a").first.get_attribute("href")

        return {
            "enseigne": "Auchan",
            "nom": nom.strip(),
            "prix": prix.strip(),
            "url": f"https://www.auchan.fr{url}" if url.startswith("/") else url
        }

    except Exception as e:
        print(f"[Auchan] Erreur : {e}")
        return {"enseigne": "Auchan", "nom": "N/A", "prix": "N/A", "url": "#"}