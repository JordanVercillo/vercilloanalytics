import requests
import pandas as pd

def fetch_products(query, page_size=10, page=1):
    """
    Fetch products matching the query from Open Food Facts.
    """
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size,
        "page": page
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}")

    data = response.json()
    return data.get("products", [])

def extract_product_fields(product):
    """
    Extract relevant fields for ML training and metadata.
    """
    nutriments = product.get("nutriments", {})
    return {
        # Identifiers
        "product_name": product.get("product_name", "N/A"),
        "brands": product.get("brands", "N/A"),
        "barcode": product.get("code", "N/A"),
        "categories": ", ".join(product.get("categories_tags", [])),
        "countries": ", ".join(product.get("countries_tags", [])),
        "image_url": product.get("image_url", "N/A"),
        "ingredients_text": product.get("ingredients_text", "N/A"),
        
        # Nutrition values
        "energy_kcal_100g": nutriments.get("energy-kcal_100g"),
        "fat_100g": nutriments.get("fat_100g"),
        "saturated_fat_100g": nutriments.get("saturated-fat_100g"),
        "carbohydrates_100g": nutriments.get("carbohydrates_100g"),
        "sugars_100g": nutriments.get("sugars_100g"),
        "fiber_100g": nutriments.get("fiber_100g"),
        "proteins_100g": nutriments.get("proteins_100g"),
        "salt_100g": nutriments.get("salt_100g"),

        # Nutrition grade and labels
        "nutrition_grade": product.get("nutrition_grades_tags", [None])[0],
        "nova_group": product.get("nova_group"),
        "ecoscore_grade": product.get("ecoscore_grade"),
        "labels": ", ".join(product.get("labels_tags", [])),
        "allergens": ", ".join(product.get("allergens_tags", [])),
        "packaging": ", ".join(product.get("packaging_tags", [])),

        # Timestamps
        "created_t": product.get("created_t"),
        "last_modified_t": product.get("last_modified_t"),
    }

def search_and_extract(query, max_pages=2, page_size=10):
    """
    Search multiple pages and extract data into a DataFrame.
    """
    all_records = []
    for page in range(1, max_pages + 1):
        print(f"Fetching page {page}...")
        products = fetch_products(query, page_size=page_size, page=page)
        if not products:
            print("No more products found.")
            break

        for product in products:
            record = extract_product_fields(product)
            all_records.append(record)

    df = pd.DataFrame(all_records)
    return df

if __name__ == "__main__":
    search_term = input("Enter search term (e.g., Oreo, Milk, Pasta): ")
    # Adjust max_pages and page_size to get more data
    df = search_and_extract(search_term, max_pages=3, page_size=20)

    # Show sample
    print("\nSample extracted data:")
    print(df.head())

    # Save to CSV
    filename = f"openfoodfacts_{search_term.replace(' ', '_')}.csv"
    df.to_csv(filename, index=False)
    print(f"\nData saved to {filename}")
