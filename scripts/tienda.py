#!/usr/bin/env python3
"""Pasito Feliz – automatización de la tienda Shopify.

Uso:
  python3 scripts/tienda.py csv      # genera productos/productos_shopify.csv para importar a mano
  python3 scripts/tienda.py setup    # crea/actualiza productos, colecciones, páginas, menús y cupón vía API

Variables de entorno para `setup`:
  SHOPIFY_STORE         p. ej. pasito-feliz.myshopify.com
  SHOPIFY_ADMIN_TOKEN   token shpat_... de una app personalizada con permisos:
                        write_products, write_content, write_online_store_navigation,
                        write_discounts, write_publications
"""
import csv
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = json.loads((ROOT / "productos" / "catalogo.json").read_text(encoding="utf-8"))
API_VERSION = "2025-07"


# ---------------------------------------------------------------- CSV export
CSV_HEADERS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Type", "Tags", "Published",
    "Option1 Name", "Option1 Value", "Variant SKU", "Variant Grams",
    "Variant Inventory Tracker", "Variant Inventory Policy", "Variant Fulfillment Service",
    "Variant Price", "Variant Compare At Price", "Variant Requires Shipping", "Variant Taxable",
    "Image Src", "Image Position", "Image Alt Text", "SEO Title", "SEO Description", "Status",
]


def export_csv():
    out = ROOT / "productos" / "productos_shopify.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for p in CATALOG["products"]:
            images = p.get("images") or [None]
            for pos, img in enumerate(images, start=1):
                row = {h: "" for h in CSV_HEADERS}
                row["Handle"] = p["handle"]
                if pos == 1:
                    row.update({
                        "Title": p["title"],
                        "Body (HTML)": p["body"],
                        "Vendor": CATALOG["vendor"],
                        "Type": p["type"],
                        "Tags": ", ".join(p["tags"]),
                        "Published": "TRUE" if p["status"] == "active" else "FALSE",
                        "Option1 Name": "Title",
                        "Option1 Value": "Default Title",
                        "Variant SKU": p["sku"],
                        "Variant Grams": p.get("grams", 0),
                        "Variant Inventory Policy": "continue",
                        "Variant Fulfillment Service": "manual",
                        "Variant Price": p["price"],
                        "Variant Compare At Price": p.get("compare_at", ""),
                        "Variant Requires Shipping": "TRUE",
                        "Variant Taxable": "TRUE",
                        "SEO Title": p.get("seo_title", ""),
                        "SEO Description": p.get("seo_description", ""),
                        "Status": p["status"],
                    })
                if img:
                    row["Image Src"] = CATALOG["image_base"] + img["file"]
                    row["Image Position"] = pos
                    row["Image Alt Text"] = img["alt"]
                writer.writerow(row)
    print(f"CSV generado: {out.relative_to(ROOT)}")


# ---------------------------------------------------------------- Admin API
def gql(query, variables=None):
    store = os.environ["SHOPIFY_STORE"].replace("https://", "").strip("/")
    req = urllib.request.Request(
        f"https://{store}/admin/api/{API_VERSION}/graphql.json",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Content-Type": "application/json", "X-Shopify-Access-Token": os.environ["SHOPIFY_ADMIN_TOKEN"]},
    )
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read())
    if body.get("errors"):
        raise RuntimeError(json.dumps(body["errors"], ensure_ascii=False))
    return body["data"]


def report(label, payload):
    errors = payload.get("userErrors") or []
    if errors:
        print(f"  ✗ {label}: {errors}")
        return False
    print(f"  ✓ {label}")
    return True


def online_store_publication():
    data = gql("{ publications(first: 20) { nodes { id name } } }")
    for pub in data["publications"]["nodes"]:
        if pub["name"] == "Online Store":
            return pub["id"]
    return None


def publish(resource_id, publication_id):
    if not publication_id:
        return
    gql(
        """mutation($id: ID!, $input: [PublicationInput!]!) {
             publishablePublish(id: $id, input: $input) { userErrors { field message } }
           }""",
        {"id": resource_id, "input": [{"publicationId": publication_id}]},
    )


def setup_products(publication_id):
    print("Productos")
    mutation = """
      mutation($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
        productSet(input: $input, identifier: $identifier, synchronous: true) {
          product { id handle status }
          userErrors { field message }
        }
      }"""
    for p in CATALOG["products"]:
        product_input = {
            "title": p["title"],
            "handle": p["handle"],
            "descriptionHtml": p["body"],
            "vendor": CATALOG["vendor"],
            "productType": p["type"],
            "tags": p["tags"],
            "status": p["status"].upper(),
            "productOptions": [{"name": "Title", "values": [{"name": "Default Title"}]}],
            "variants": [{
                "optionValues": [{"optionName": "Title", "name": "Default Title"}],
                "price": p["price"],
                "sku": p["sku"],
                "inventoryPolicy": "CONTINUE",
            }],
        }
        if p.get("seo_title"):
            product_input["seo"] = {"title": p["seo_title"], "description": p.get("seo_description", "")}
        if p.get("images"):
            product_input["files"] = [
                {"originalSource": CATALOG["image_base"] + img["file"], "alt": img["alt"], "contentType": "IMAGE"}
                for img in p["images"]
            ]
        data = gql(mutation, {"input": product_input, "identifier": {"handle": p["handle"]}})["productSet"]
        if report(p["title"], data) and data["product"]:
            publish(data["product"]["id"], publication_id)


def setup_collections(publication_id):
    print("Colecciones")
    for c in CATALOG["collections"]:
        existing = gql("query($h: String!) { collectionByHandle(handle: $h) { id } }", {"h": c["handle"]})
        if existing["collectionByHandle"]:
            print(f"  = {c['title']} (ya existe)")
            continue
        data = gql(
            """mutation($input: CollectionInput!) {
                 collectionCreate(input: $input) { collection { id } userErrors { field message } }
               }""",
            {"input": {
                "title": c["title"],
                "handle": c["handle"],
                "descriptionHtml": f"<p>{c['description']}</p>",
                "ruleSet": {"appliedDisjunctively": False,
                            "rules": [{"column": "TAG", "relation": "EQUALS", "condition": c["tag"]}]},
            }},
        )["collectionCreate"]
        if report(c["title"], data):
            publish(data["collection"]["id"], publication_id)


def setup_pages():
    print("Páginas")
    existing = {n["handle"] for n in gql("{ pages(first: 100) { nodes { handle } } }")["pages"]["nodes"]}
    for page in CATALOG["pages"]:
        if page["handle"] in existing:
            print(f"  = {page['title']} (ya existe)")
            continue
        body = (ROOT / "contenido" / "paginas" / page["file"]).read_text(encoding="utf-8")
        data = gql(
            """mutation($page: PageCreateInput!) {
                 pageCreate(page: $page) { page { id } userErrors { field message } }
               }""",
            {"page": {"title": page["title"], "handle": page["handle"], "body": body, "isPublished": True}},
        )["pageCreate"]
        report(page["title"], data)


MENUS = {
    "main-menu": ("Menú principal", [
        ("Inicio", "/"),
        ("Protector de cabeza", "/products/protector-cabeza-bebe-abejita"),
        ("Seguridad", "/collections/seguridad-bebe"),
        ("Primeros pasos", "/collections/primeros-pasos"),
        ("Hora de dormir", "/collections/hora-de-dormir"),
        ("Alimentación", "/collections/alimentacion"),
    ]),
    "footer": ("Ayuda", [
        ("Nuestra historia", "/pages/nosotros"),
        ("Envíos y pago contra entrega", "/pages/envios"),
        ("Cambios y devoluciones", "/pages/cambios-y-devoluciones"),
        ("Contacto", "/pages/contacto"),
        ("Buscar", "/search"),
    ]),
}


def setup_menus():
    print("Menús")
    existing = {n["handle"]: n["id"] for n in gql("{ menus(first: 50) { nodes { id handle } } }")["menus"]["nodes"]}
    for handle, (title, links) in MENUS.items():
        items = [{"title": t, "type": "HTTP", "url": u} for t, u in links]
        if handle in existing:
            data = gql(
                """mutation($id: ID!, $title: String!, $handle: String, $items: [MenuItemUpdateInput!]!) {
                     menuUpdate(id: $id, title: $title, handle: $handle, items: $items) { userErrors { field message } }
                   }""",
                {"id": existing[handle], "title": title, "handle": handle, "items": items},
            )["menuUpdate"]
        else:
            data = gql(
                """mutation($title: String!, $handle: String!, $items: [MenuItemCreateInput!]!) {
                     menuCreate(title: $title, handle: $handle, items: $items) { userErrors { field message } }
                   }""",
                {"title": title, "handle": handle, "items": items},
            )["menuCreate"]
        report(title, data)


def setup_discounts():
    print("Cupones")
    for d in CATALOG["discounts"]:
        found = gql("query($c: String!) { codeDiscountNodeByCode(code: $c) { id } }", {"c": d["code"]})
        if found["codeDiscountNodeByCode"]:
            print(f"  = {d['code']} (ya existe)")
            continue
        data = gql(
            """mutation($d: DiscountCodeBasicInput!) {
                 discountCodeBasicCreate(basicCodeDiscount: $d) { userErrors { field message } }
               }""",
            {"d": {
                "title": d["title"],
                "code": d["code"],
                "startsAt": datetime.now(timezone.utc).isoformat(),
                "context": {"all": "ALL"},
                "customerGets": {"value": {"percentage": d["percentage"]}, "items": {"all": True}},
                "appliesOncePerCustomer": True,
            }},
        )["discountCodeBasicCreate"]
        report(d["code"], data)


def setup():
    for var in ("SHOPIFY_STORE", "SHOPIFY_ADMIN_TOKEN"):
        if not os.environ.get(var):
            sys.exit(f"Falta la variable de entorno {var}")
    publication_id = online_store_publication()
    setup_products(publication_id)
    setup_collections(publication_id)
    setup_pages()
    setup_menus()
    setup_discounts()
    print("Listo ✔")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "csv":
        export_csv()
    elif command == "setup":
        setup()
    else:
        sys.exit(__doc__)
