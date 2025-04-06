import asyncio
from playwright.async_api import async_playwright
import logging
import json
import time
import os
import random
from datetime import datetime
import aiohttp
from typing import List, Dict, Optional
import sys
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('supreme_monitor.log'),
        logging.StreamHandler()
    ]
)

class SupremeBot:
    def __init__(self):
        self.base_url = "https://eu.supreme.com"
        self.shop_url = "https://eu.supreme.com/pages/shop"
        self.api_endpoints = {
            'shop_all': f"{self.base_url}/shop/all.json",
            'shop_new': f"{self.base_url}/shop/new.json",
            'categories': [
                f"{self.base_url}/shop/all/jackets.json",
                f"{self.base_url}/shop/all/shirts.json",
                f"{self.base_url}/shop/all/tops_sweaters.json",
                f"{self.base_url}/shop/all/sweatshirts.json",
                f"{self.base_url}/shop/all/pants.json",
                f"{self.base_url}/shop/all/shorts.json",
                f"{self.base_url}/shop/all/t-shirts.json",
                f"{self.base_url}/shop/all/hats.json",
                f"{self.base_url}/shop/all/bags.json",
                f"{self.base_url}/shop/all/accessories.json",
                f"{self.base_url}/shop/all/shoes.json",
                f"{self.base_url}/shop/all/skate.json"
            ]
        }
        self.setup_directories()
        self.load_data()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.stats = {
            "requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "variants_found": 0,
            "new_products": 0
        }
        self.retry_count = 0
        self.max_retries = 3
        self.check_interval = 600  # Check every 10 minutes (600 seconds)

    def setup_directories(self):
        """Create necessary directories for storing data and screenshots"""
        self.dirs = {
            'data': 'supreme_data',
            'variants': 'supreme_variants',
            'logs': 'supreme_logs',
            'debug': 'supreme_debug',
            'screenshots': 'product_screenshots'
        }
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)

    def load_data(self):
        """Load existing product and variant data"""
        self.products_file = os.path.join(self.dirs['data'], 'products.json')
        self.variants_file = os.path.join(self.dirs['data'], 'variants.json')
        
        try:
            with open(self.products_file, 'r') as f:
                self.products = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.products = {}
        
        try:
            with open(self.variants_file, 'r') as f:
                self.variants = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.variants = {}

    async def setup_browser(self):
        """Initialize browser with enhanced anti-detection measures"""
        self.playwright = await async_playwright().start()
        
        browser_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process,CrossSiteDocumentBlockingIfIsolating',
            '--disable-site-isolation-trials',
            '--disable-web-security',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            f'--window-size={random.randint(1050, 1200)},{random.randint(800, 900)}',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--hide-scrollbars',
            '--disable-notifications',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-breakpad',
            '--disable-component-extensions-with-background-pages',
            '--disable-extensions',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--disable-renderer-backgrounding',
            '--enable-features=NetworkService,NetworkServiceInProcess',
            '--force-color-profile=srgb',
            '--metrics-recording-only',
            '--mute-audio',
            '--disable-javascript-harmony-shipping',
            '--no-default-browser-check',
            '--no-experiments',
            '--no-pings',
            '--no-zygote',
            '--password-store=basic'
        ]

        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=browser_args
        )

        # Enhanced context configuration
        self.context = await self.browser.new_context(
            viewport={'width': random.randint(1050, 1200), 'height': random.randint(800, 900)},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            color_scheme='dark',
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            ignore_https_errors=True,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Cache-Control': 'max-age=0'
            }
        )

        # Enhanced stealth scripts
        await self.context.add_init_script("""
            const originalFunction = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                if (type === 'image/png' && this.width === 220 && this.height === 30) {
                    return originalFunction.apply(this, arguments);
                }
            }
            
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [
                {description: "Portable Document Format",name: "PDF Viewer",filename: "internal-pdf-viewer"},
                {description: "Portable Document Format",name: "Chrome PDF Viewer",filename: "internal-pdf-viewer"},
                {description: "Portable Document Format",name: "Chromium PDF Viewer",filename: "internal-pdf-viewer"},
                {description: "Portable Document Format",name: "Microsoft Edge PDF Viewer",filename: "internal-pdf-viewer"},
                {description: "Portable Document Format",name: "WebKit built-in PDF",filename: "internal-pdf-viewer"}
            ]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({state: Notification.permission}) :
                originalQuery(parameters)
            );
        """)

        self.page = await self.context.new_page()
        await self.setup_request_interception()

    async def setup_request_interception(self):
        """Setup request interception to modify headers and handle responses"""
        await self.page.route("**/*", self.handle_request)

    async def handle_request(self, route):
        """Handle and modify requests"""
        request = route.request
        headers = {**request.headers}
        
        # Add dynamic headers
        headers.update({
            'X-Requested-With': 'XMLHttpRequest',
            'X-Timestamp': str(int(time.time())),
            'X-Request-ID': f'{random.randint(1000000, 9999999)}',
        })

        try:
            await route.continue_(headers=headers)
        except Exception as e:
            logging.error(f"Error in request handling: {str(e)}")
            await route.continue_()

    async def simulate_human_behavior(self):
        """Enhanced human-like behavior simulation"""
        try:
            # Randomized mouse movements
            for _ in range(random.randint(3, 7)):
                # Bezier curve-like movement
                points = [(random.randint(100, 800), random.randint(100, 600)) for _ in range(3)]
                for x, y in points:
                    await self.page.mouse.move(x, y, steps=random.randint(5, 10))
                    await asyncio.sleep(random.uniform(0.1, 0.3))

            # Natural scrolling pattern
            scroll_points = [
                random.randint(300, 700),
                random.randint(500, 1000),
                random.randint(200, 400)
            ]
            
            for scroll_amount in scroll_points:
                await self.page.mouse.wheel(0, scroll_amount)
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
            # Random clicks (avoiding buttons)
            for _ in range(random.randint(1, 3)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                await self.page.mouse.click(x, y)
                await asyncio.sleep(random.uniform(0.5, 1.0))

            # Variable pauses
            await asyncio.sleep(random.uniform(1, 3))

        except Exception as e:
            logging.error(f"Error in human behavior simulation: {str(e)}")

    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if hasattr(self, 'page') and self.page:
                await self.page.close()
            if hasattr(self, 'context') and self.context:
                await self.context.close()
            if hasattr(self, 'browser') and self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")

    async def bypass_cloudflare(self):
        """Bypass Cloudflare protection"""
        try:
            # First try to access the main page
            await self.page.goto(self.base_url, wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(random.randint(2000, 3000))
            
            # Simulate human-like behavior
            await self.page.mouse.move(
                random.randint(100, 700),
                random.randint(100, 500)
            )
            await self.page.mouse.wheel(delta_x=0, delta_y=random.randint(300, 500))
            await self.page.wait_for_timeout(random.randint(1000, 2000))
            
            # Navigate to shop URL
            await self.page.goto(self.shop_url, wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(random.randint(2000, 3000))
            
            # Try multiple selectors for products
            selectors = [
                'article[data-product]',
                '.product-item',
                '.product-grid-item',
                '[data-product-id]',
                '.product-card'
            ]
            
            for selector in selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    logging.info(f"Found products using selector: {selector}")
                    return True
                except:
                    continue
            
            # If no products found, try to navigate to all products
            try:
                await self.page.goto(f"{self.shop_url}/all", wait_until='domcontentloaded', timeout=60000)
                await self.page.wait_for_timeout(random.randint(2000, 3000))
                
                # Try selectors again
                for selector in selectors:
                    try:
                        await self.page.wait_for_selector(selector, timeout=5000)
                        logging.info(f"Found products using selector: {selector}")
                        return True
                    except:
                        continue
            except Exception as e:
                logging.error(f"Error navigating to all products: {str(e)}")
            
            return False
        except Exception as e:
            logging.error(f"Error bypassing Cloudflare: {str(e)}")
            return False

    async def fetch_products_from_category(self, category):
        """Fetch products from a specific category"""
        try:
            url = f"{self.shop_url}/{category}"
            logging.info(f"Fetching products from category: {category}")
            
            # Navigate to category page
            await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await self.page.wait_for_timeout(random.randint(2000, 3000))
            
            # Scroll to load all products
            await self.page.evaluate("""
                async () => {
                    const scrollHeight = document.body.scrollHeight;
                    const viewportHeight = window.innerHeight;
                    let currentPosition = 0;
                    
                    while (currentPosition < scrollHeight) {
                        window.scrollTo(0, currentPosition);
                        currentPosition += viewportHeight;
                        await new Promise(resolve => setTimeout(resolve, 500));
                    }
                    
                    // Scroll back to top
                    window.scrollTo(0, 0);
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            """)
            
            # Wait for products to load
            await self.page.wait_for_selector('article[data-product]', timeout=10000)
            
            # Extract product data
            products = await self.page.evaluate("""
                () => {
                    const products = [];
                    document.querySelectorAll('article[data-product]').forEach(article => {
                        const product = {
                            id: article.getAttribute('data-product-id'),
                            name: article.querySelector('h1, h2, h3').textContent.trim(),
                            price: article.querySelector('.price').textContent.trim(),
                            image: article.querySelector('img').src,
                            variants: []
                        };
                        
                        // Extract variants
                        const variantElements = article.querySelectorAll('[data-variant]');
                        variantElements.forEach(variant => {
                            product.variants.push({
                                id: variant.getAttribute('data-variant-id'),
                                size: variant.getAttribute('data-size'),
                                color: variant.getAttribute('data-color'),
                                price: variant.getAttribute('data-price')
                            });
                        });
                        
                        // If no variants found, try to extract from product page
                        if (product.variants.length === 0) {
                            const variantData = article.getAttribute('data-variants');
                            if (variantData) {
                                try {
                                    const variants = JSON.parse(variantData);
                                    product.variants = variants;
                                } catch (e) {}
                            }
                        }
                        
                        products.push(product);
                    });
                    return products;
                }
            """)
            
            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(self.dirs['debug'], f"{category}_{timestamp}.png")
            await self.page.screenshot(path=screenshot_path, full_page=True)
            
            return products
        except Exception as e:
            logging.error(f"Error fetching category {category}: {str(e)}")
            return []

    async def check_backend_endpoints(self) -> List[Dict]:
        """Check various backend endpoints for upcoming products"""
        all_products = []
        
        # First check main endpoints
        for endpoint_name in ['shop_all', 'shop_new']:
            try:
                url = self.api_endpoints[endpoint_name]
                logging.info(f"Checking endpoint: {endpoint_name}")
                
                # Use fetch API instead of navigation
                js_code = """
                async (url) => {
                    try {
                        const response = await fetch(url, {
                            method: 'GET',
                            headers: {
                                'Accept': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                            }
                        });
                        if (!response.ok) return null;
                        return await response.json();
                    } catch (e) {
                        return null;
                    }
                }
                """
                result = await self.page.evaluate(js_code, url)
                
                if result:
                    products = result.get('products', [])
                    for product in products:
                        product['_source'] = endpoint_name
                        product['_timestamp'] = datetime.now().isoformat()
                        all_products.append(product)
                        
                        # Extract variants immediately
                        if 'handle' in product:
                            variants = await self.extract_product_variants(product['handle'])
                            product['variants'] = variants
                
            except Exception as e:
                logging.error(f"Error checking {endpoint_name}: {str(e)}")
                continue
        
        # Then check category endpoints
        for category_url in self.api_endpoints['categories']:
            try:
                category_name = category_url.split('/')[-1].replace('.json', '')
                logging.info(f"Checking category: {category_name}")
                
                js_code = """
                async (url) => {
                    try {
                        const response = await fetch(url, {
                            method: 'GET',
                            headers: {
                                'Accept': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                            }
                        });
                        if (!response.ok) return null;
                        return await response.json();
                    } catch (e) {
                        return null;
                    }
                }
                """
                result = await self.page.evaluate(js_code, category_url)
                
                if result:
                    products = result.get('products', [])
                    for product in products:
                        product['_source'] = f"category_{category_name}"
                        product['_timestamp'] = datetime.now().isoformat()
                        all_products.append(product)
                        
                        # Extract variants immediately
                        if 'handle' in product:
                            variants = await self.extract_product_variants(product['handle'])
                            product['variants'] = variants
                
            except Exception as e:
                logging.error(f"Error checking category {category_name}: {str(e)}")
                continue
        
        return all_products

    async def extract_product_variants(self, product_handle: str) -> Dict:
        """Extract variant information from a product page"""
        try:
            url = f"{self.base_url}/shop/{product_handle}.json"
            logging.info(f"Fetching variants for {product_handle} from {url}")

            js_code = """
            async (url) => {
                try {
                    const response = await fetch(url, {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                        }
                    });
                    if (!response.ok) return null;
                    return await response.json();
                } catch (e) {
                    return null;
                }
            }
            """
            result = await self.page.evaluate(js_code, url)

            if result and 'styles' in result:
                variants = {}
                for style in result['styles']:
                    style_name = style.get('name')
                    for size in style.get('sizes', []):
                        key = f"{style_name} - {size.get('name')}"
                        variants[key] = {
                            'id': size.get('id'),
                            'stock_level': size.get('stock_level'),
                            'available': size.get('stock_level', 0) > 0
                        }
                return variants
            return {}
        except Exception as e:
            logging.error(f"Error extracting variants for {product_handle}: {str(e)}")
            return {}

    async def monitor_all_categories(self):
        """Monitor all product categories"""
        try:
            for category in self.api_endpoints['categories']:
                logging.info(f"\n=== Monitoring category: {category} ===")
                
                # Navigate to category page
                url = f"{self.shop_url}/{category}"
                await self.page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await self.page.wait_for_timeout(random.randint(2000, 3000))
                
                # Scroll to load all products
                await self.page.evaluate("""
                    async () => {
                        const scrollHeight = document.body.scrollHeight;
                        const viewportHeight = window.innerHeight;
                        let currentPosition = 0;
                        
                        while (currentPosition < scrollHeight) {
                            window.scrollTo(0, currentPosition);
                            currentPosition += viewportHeight;
                            await new Promise(resolve => setTimeout(resolve, 500));
                        }
                        
                        // Scroll back to top
                        window.scrollTo(0, 0);
                        await new Promise(resolve => setTimeout(resolve, 1000));
                    }
                """)
                
                # Take screenshot of the category page
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(self.dirs['screenshots'], f"{category}_{timestamp}.png")
                await self.page.screenshot(path=screenshot_path, full_page=True)
                logging.info(f"Saved screenshot: {screenshot_path}")
                
                # Extract products and variants
                products = await self.extract_products_from_page()
                if products:
                    logging.info(f"Found {len(products)} products in category {category}")
                    
                    # Process each product
                    for product in products:
                        # Extract variants
                        variants = await self.extract_product_variants(product['handle'])
                        product['variants'] = variants
                        
                        # Save product data
                        self.save_product_data(product, category)
                        
                        # Log product details
                        logging.info(f"Product: {product['title']}")
                        logging.info(f"Price: {product['price']}")
                        logging.info(f"Variants: {len(variants)}")
                        
                        # Take screenshot of product page
                        product_screenshot_path = os.path.join(
                            self.dirs['screenshots'],
                            f"product_{product['handle']}_{timestamp}.png"
                        )
                        await self.page.screenshot(path=product_screenshot_path, full_page=True)
                
                # Wait before next category
                await asyncio.sleep(random.randint(2, 4))
                
        except Exception as e:
            logging.error(f"Error monitoring categories: {str(e)}")

    async def extract_products_from_page(self):
        """Extract products from the current page"""
        try:
            products = await self.page.evaluate("""
                () => {
                    const products = [];
                    document.querySelectorAll('article[data-product]').forEach(article => {
                        const product = {
                            id: article.getAttribute('data-product-id'),
                            handle: article.getAttribute('data-product-handle'),
                            title: article.querySelector('h1, h2, h3').textContent.trim(),
                            price: article.querySelector('.price').textContent.trim(),
                            image: article.querySelector('img').src,
                            variants: []
                        };
                        products.push(product);
                    });
                    return products;
                }
            """)
            return products
        except Exception as e:
            logging.error(f"Error extracting products: {str(e)}")
            return []

    def save_product_data(self, product, category):
        """Save product data to JSON files"""
        try:
            # Save to products file
            products_file = os.path.join(self.dirs['data'], 'products.json')
            if os.path.exists(products_file):
                with open(products_file, 'r') as f:
                    products_data = json.load(f)
            else:
                products_data = {}
            
            products_data[product['id']] = {
                'title': product['title'],
                'price': product['price'],
                'category': category,
                'handle': product['handle'],
                'image': product['image'],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(products_file, 'w') as f:
                json.dump(products_data, f, indent=2)
            
            # Save to variants file
            variants_file = os.path.join(self.dirs['variants'], f"{product['id']}_variants.json")
            with open(variants_file, 'w') as f:
                json.dump({
                    'product_id': product['id'],
                    'product_title': product['title'],
                    'variants': product['variants'],
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            
            logging.info(f"Saved data for product: {product['title']}")
            
        except Exception as e:
            logging.error(f"Error saving product data: {str(e)}")

    async def monitor_variants(self):
        """Monitor backend for new products and variants"""
        try:
            await self.setup_browser()
            if not await self.bypass_cloudflare():
                return
            
            while True:
                start_time = time.time()
                logging.info(f"\n=== Starting monitoring cycle at {datetime.now()} ===")
                
                # Monitor all categories
                await self.monitor_all_categories()
                
                # Log statistics
                self.log_statistics(start_time)
                
                # Wait for 10 minutes before next check
                logging.info("Waiting for 10 minutes before next check...")
                await asyncio.sleep(self.check_interval)
                
        except Exception as e:
            logging.error(f"Monitor error: {str(e)}")
        finally:
            await self.cleanup()

    def log_statistics(self, start_time: float):
        """Log monitoring statistics"""
        runtime = time.time() - start_time
        
        logging.info("\n=== Monitoring Statistics ===")
        logging.info(f"Runtime: {runtime:.2f} seconds")
        logging.info(f"New Products Found: {self.stats['new_products']}")
        logging.info(f"New Variants Found: {self.stats['variants_found']}")
        logging.info("===========================\n")

async def main():
    """Main entry point"""
    try:
        bot = SupremeBot()
        await bot.monitor_variants()
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 