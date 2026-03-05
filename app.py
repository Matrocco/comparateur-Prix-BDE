import asyncio
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from playwright.async_api import async_playwright

# Import de tes scrapers (assure-toi que les fichiers existent dans /scrapers)
from scrapers.auchan import scrape_auchan
# from scrapers.carrefour import scrape_carrefour
# from scrapers.intermarche import scrape_intermarche

app = FastAPI()

# Configuration des fichiers statiques et des templates HTML
# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    """Affiche la page d'accueil avec la barre de recherche."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chercher")
async def chercher(request: Request, produit: str = Form(...)):
    """Lance la recherche sur tous les sites en parallèle."""
    
    resultats = []
    
    async with async_playwright() as p:
        # Lancement du navigateur (indispensable pour Docker)
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # On lance les tâches en parallèle pour gagner du temps
        # Pour l'instant on active Auchan, tu décommenteras les autres au fur et à mesure
        tasks = [
            scrape_auchan(page, produit),
            # scrape_carrefour(page, produit),
            # scrape_intermarche(page, produit)
        ]
        
        # gather permet d'attendre que tous les scrapers aient fini
        reponses = await asyncio.gather(*tasks)
        
        # On filtre les résultats vides ou erreurs
        resultats = [r for r in reponses if r and r.get("prix") != "N/A"]
        
        # Tri par prix (du moins cher au plus cher)
        # On nettoie la chaîne "2,50€" pour la transformer en float 2.50 pour le tri
        try:
            resultats.sort(key=lambda x: float(x['prix'].replace('€', '').replace(',', '.').strip()))
        except:
            pass

        await browser.close()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "resultats": resultats,
        "produit_cherche": produit
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
