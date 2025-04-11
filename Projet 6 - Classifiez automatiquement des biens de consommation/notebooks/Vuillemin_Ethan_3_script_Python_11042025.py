#%%
import requests
import csv

# Documentation:
# https://ensip.gitlab.io/pages-info/ressources/transverse/tuto_apiweb/#openfoodfacts
# https://fr.openfoodfacts.org/data

# Exemple de requetes:
# https://world.openfoodfacts.org/cgi/search.pl?search_terms=champagne&search_simple=1&action=process&json=1
# https://world.openfoodfacts.org/cgi/search.pl?search_terms=champignon&page_size=10&json=1

# Setup les parms de la query
url = "https://world.openfoodfacts.org/cgi/search.pl"
params = {
    "search_terms": "champagne",
    "page_size": 10,
    "json": 1
}
# faire la requete
response = requests.get(url, params=params)
data = response.json()
#%%
# Recuperer les champs qui nous interessent
products = []
for product in data.get("products", []):
    food_id = product.get("_id", "")
    label = product.get("product_name", "")
    category = product.get("categories", "")
    food_contents_label = product.get("ingredients_text", "")
    image = product.get("image_front_url", "")
    
    products.append({
        "foodId": food_id,
        "label": label,
        "category": category,
        "foodContentsLabel": food_contents_label,
        "image": image
    })

# Creation du fichier CSV
csv_filename = f"produits_{params['search_terms']}.csv"
csv_headers = ["foodId", "label", "category", "foodContentsLabel", "image"]

with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()
    writer.writerows(products)

print(f"Les données ont été exportées dans le fichier '{csv_filename}'.")
# %%
