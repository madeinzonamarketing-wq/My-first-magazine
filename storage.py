import json
import os
import aiofiles

PRODUCTS_FILE = "products.json"

async def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    async with aiofiles.open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        content = await f.read()
        return json.loads(content) if content else []

async def save_products(products):
    async with aiofiles.open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(products, ensure_ascii=False, indent=2))

async def add_product(product):
    products = await load_products()
    product["id"] = max([p.get("id", 0) for p in products], default=0) + 1
    products.append(product)
    await save_products(products)
    return product["id"]

async def update_product(prod_id, updates):
    products = await load_products()
    for p in products:
        if p.get("id") == prod_id:
            p.update(updates)
            await save_products(products)
            return True
    return False

async def delete_product(prod_id):
    products = await load_products()
    products = [p for p in products if p.get("id") != prod_id]
    await save_products(products)
