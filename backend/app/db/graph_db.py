"""
Neo4j Graph Database integration for product relationships.

This module handles:
- Product nodes and relationships
- Category hierarchies
- Product comparisons
- Accessory compatibility
- Specifications lookup
"""

import os
from typing import List, Dict, Any, Optional
import logging
from neo4j import GraphDatabase as Neo4jDriver
import json

logger = logging.getLogger(__name__)


class GraphDatabase:
    """Neo4j graph database manager for product relationships."""

    def __init__(self):
        """Initialize graph database connection."""
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password123")
        self.driver = None
        self.data_path = "./data"

    async def initialize(self):
        """Initialize connection and seed data."""
        logger.info(f"🔌 Connecting to Neo4j at {self.uri}...")

        try:
            self.driver = Neo4jDriver.driver(self.uri, auth=(self.user, self.password))

            # Verify connection
            self.driver.verify_connectivity()
            logger.info("✅ Connected to Neo4j")

            # Check if data exists
            if not await self._has_data():
                logger.info("🌱 Seeding graph database...")
                await self.seed_data()
            else:
                logger.info("✅ Graph database already contains data")

        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            logger.warning("⚠️  Running without graph database functionality")
            self.driver = None

    async def close(self):
        """Close database connection."""
        if self.driver:
            self.driver.close()
            logger.info("👋 Neo4j connection closed")

    async def _has_data(self) -> bool:
        """Check if graph already has data."""
        if not self.driver:
            return False

        try:
            with self.driver.session() as session:
                result = session.run("MATCH (p:Product) RETURN count(p) as count")
                record = result.single()
                return record and record["count"] > 0
        except Exception as e:
            logger.error(f"❌ Error checking graph data: {e}")
            return False

    async def seed_data(self):
        """Seed graph database with product data."""
        if not self.driver:
            logger.warning("⚠️  No Neo4j driver available")
            return

        try:
            # Load products
            products_file = os.path.join(self.data_path, "products.json")
            if not os.path.exists(products_file):
                logger.warning(f"⚠️  Products file not found: {products_file}")
                return

            with open(products_file, "r") as f:
                products = json.load(f)

            with self.driver.session() as session:
                # Clear existing data
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("🗑️  Cleared existing graph data")

                # Create products and categories
                for product in products:
                    self._create_product_node(session, product)

                # Create relationships
                self._create_relationships(session, products)

                logger.info(f"✅ Seeded {len(products)} products to graph database")

        except Exception as e:
            logger.error(f"❌ Error seeding graph database: {e}")

    def _create_product_node(self, session, product: Dict[str, Any]):
        """Create product node with properties."""
        query = """
        CREATE (p:Product {
            id: $id,
            name: $name,
            category: $category,
            brand: $brand,
            price: $price,
            description: $description,
            in_stock: $in_stock,
            warranty: $warranty,
            rating: $rating
        })
        """

        session.run(
            query,
            **{
                "id": product["id"],
                "name": product["name"],
                "category": product["category"],
                "brand": product.get("brand", ""),
                "price": product["price"],
                "description": product.get("description", ""),
                "in_stock": product.get("in_stock", True),
                "warranty": product.get("warranty", ""),
                "rating": product.get("rating", 0.0),
            },
        )

        # Create specs as separate nodes
        specs = product.get("specs", {})
        if specs:
            self._create_spec_nodes(session, product["id"], specs)

    def _create_spec_nodes(self, session, product_id: int, specs: Dict[str, Any]):
        """Create specification nodes linked to product."""
        for key, value in specs.items():
            if value:
                query = """
                MATCH (p:Product {id: $product_id})
                CREATE (s:Spec {key: $key, value: $value})
                CREATE (p)-[:HAS_SPEC]->(s)
                """
                session.run(query, product_id=product_id, key=key, value=str(value))

    def _create_relationships(self, session, products: List[Dict[str, Any]]):
        """Create relationships between products."""
        # Same category relationships
        categories = {}
        for product in products:
            category = product["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(product["id"])

        for category, product_ids in categories.items():
            for i, pid1 in enumerate(product_ids):
                for pid2 in product_ids[i + 1 :]:
                    query = """
                    MATCH (p1:Product {id: $pid1})
                    MATCH (p2:Product {id: $pid2})
                    CREATE (p1)-[:SAME_CATEGORY]->(p2)
                    CREATE (p2)-[:SAME_CATEGORY]->(p1)
                    """
                    session.run(query, pid1=pid1, pid2=pid2)

        # Compatibility relationships (example: laptops compatible with accessories)
        # In real system, this would be based on actual compatibility data
        self._create_compatibility_relationships(session, products)

    def _create_compatibility_relationships(
        self, session, products: List[Dict[str, Any]]
    ):
        """Create compatibility relationships between products."""
        # Example: Create compatibility between laptops and accessories
        laptops = [p for p in products if p["category"] == "Laptops"]
        accessories = [
            p for p in products if p["category"] in ["Accessories", "Peripherals"]
        ]

        for laptop in laptops:
            # Compatible with USB-C accessories if laptop has USB-C
            specs = laptop.get("specs", {})
            ports = specs.get("ports", [])

            if isinstance(ports, list) and "USB-C" in ports:
                for accessory in accessories:
                    if "USB-C" in accessory.get("name", ""):
                        query = """
                        MATCH (p1:Product {id: $pid1})
                        MATCH (p2:Product {id: $pid2})
                        CREATE (p1)-[:COMPATIBLE_WITH]->(p2)
                        """
                        session.run(query, pid1=laptop["id"], pid2=accessory["id"])

    async def compare_products(self, product_ids: List[int]) -> Dict[str, Any]:
        """
        Compare multiple products using graph queries.

        Args:
            product_ids: List of product IDs to compare

        Returns:
            Comparison result with products and differences
        """
        if not self.driver:
            return await self._fallback_comparison(product_ids)

        try:
            with self.driver.session() as session:
                # Get products
                query = """
                MATCH (p:Product)
                WHERE p.id IN $product_ids
                OPTIONAL MATCH (p)-[:HAS_SPEC]->(s:Spec)
                RETURN p, collect({key: s.key, value: s.value}) as specs
                """

                result = session.run(query, product_ids=product_ids)

                products = []
                all_specs = set()

                for record in result:
                    product = dict(record["p"])
                    specs = {s["key"]: s["value"] for s in record["specs"] if s["key"]}
                    product["specs"] = specs
                    products.append(product)
                    all_specs.update(specs.keys())

                # Create comparison
                comparison = []
                for spec_key in all_specs:
                    values = {}
                    for product in products:
                        values[product["name"]] = product["specs"].get(spec_key, "N/A")

                    comparison.append({"feature": spec_key, "values": values})

                # Add basic info comparison
                for field in ["price", "rating", "warranty"]:
                    values = {}
                    for product in products:
                        values[product["name"]] = product.get(field, "N/A")

                    comparison.append({"feature": field, "values": values})

                return {
                    "products": products,
                    "comparison": comparison,
                    "recommendation": self._generate_recommendation(products),
                }

        except Exception as e:
            logger.error(f"❌ Error comparing products: {e}")
            return await self._fallback_comparison(product_ids)

    async def _fallback_comparison(self, product_ids: List[int]) -> Dict[str, Any]:
        """Fallback comparison without graph database."""
        # Load products from JSON
        products_file = os.path.join(self.data_path, "products.json")

        try:
            with open(products_file, "r") as f:
                all_products = json.load(f)

            products = [p for p in all_products if p["id"] in product_ids]

            if not products:
                return {
                    "products": [],
                    "comparison": [],
                    "recommendation": "Products not found.",
                }

            # Simple comparison
            comparison = []

            # Compare specs
            all_spec_keys = set()
            for p in products:
                if "specs" in p and p["specs"]:
                    all_spec_keys.update(p["specs"].keys())

            for spec_key in all_spec_keys:
                values = {}
                for p in products:
                    spec_value = p.get("specs", {}).get(spec_key, "N/A")
                    values[p["name"]] = spec_value

                comparison.append({"feature": spec_key, "values": values})

            # Compare basic fields
            for field in ["price", "rating", "warranty"]:
                values = {}
                for p in products:
                    values[p["name"]] = p.get(field, "N/A")

                comparison.append({"feature": field, "values": values})

            return {
                "products": products,
                "comparison": comparison,
                "recommendation": self._generate_recommendation(products),
            }

        except Exception as e:
            logger.error(f"❌ Error in fallback comparison: {e}")
            return {
                "products": [],
                "comparison": [],
                "recommendation": "Unable to compare products.",
            }

    def _generate_recommendation(self, products: List[Dict[str, Any]]) -> str:
        """Generate simple recommendation based on products."""
        if not products:
            return ""

        if len(products) == 1:
            return f"{products[0]['name']} is a great choice!"

        # Simple logic: recommend highest rated
        best_product = max(products, key=lambda p: p.get("rating", 0))

        return (
            f"Based on ratings and features, {best_product['name']} "
            f"(rated {best_product.get('rating', 0)}/5) appears to be the best option."
        )

    async def find_compatible_products(self, product_id: int) -> List[Dict[str, Any]]:
        """Find products compatible with given product."""
        if not self.driver:
            return []

        try:
            with self.driver.session() as session:
                query = """
                MATCH (p1:Product {id: $product_id})-[:COMPATIBLE_WITH]->(p2:Product)
                RETURN p2
                """

                result = session.run(query, product_id=product_id)
                return [dict(record["p2"]) for record in result]

        except Exception as e:
            logger.error(f"❌ Error finding compatible products: {e}")
            return []
