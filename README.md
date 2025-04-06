# Supreme Bot

A powerful automated bot for monitoring Supreme products, variants, and stock levels. This bot uses Playwright for browser automation and provides comprehensive monitoring capabilities.

## Features

- 🔍 Monitor all Supreme product categories
- 📊 Track product variants and stock levels
- 📸 Automatic screenshot capture
- 📝 Detailed logging of all activities
- 🔄 10-minute monitoring intervals
- 🛡️ Anti-detection measures
- 🌐 Cloudflare bypass
- 💾 Data persistence in JSON format

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

## Project Structure

```
supreme-bot/
├── supreme_bot.py          # Main bot implementation
├── requirements.txt        # Project dependencies
├── supreme_data/          # Product data storage
├── supreme_variants/      # Variant data storage
├── supreme_logs/          # Log files
├── supreme_debug/         # Debug information
└── product_screenshots/   # Screenshots of products
```

## Usage

1. Run the bot:
```bash
python supreme_bot.py
```

2. The bot will:
   - Monitor all product categories
   - Extract variant information
   - Save screenshots and data
   - Log all activities
   - Run checks every 10 minutes

## Configuration

The bot includes several configurable parameters:

- `check_interval`: Time between checks (default: 600 seconds)
- `max_retries`: Maximum number of retry attempts
- `base_url`: Supreme website URL
- `shop_url`: Supreme shop URL

## Dependencies

- `playwright==1.42.0`: Browser automation
- `aiohttp==3.9.3`: Async HTTP requests
- `python-dotenv==1.0.1`: Environment variables
- `beautifulsoup4==4.12.3`: HTML parsing
- `requests==2.31.0`: HTTP requests
- `lxml==5.1.0`: XML/HTML parsing
- `pillow==10.2.0`: Image processing
- `python-dateutil==2.8.2`: Date/time handling

## Features in Detail

### Monitoring
- Checks all product categories
- Tracks new products and variants
- Monitors stock levels
- Saves product data and screenshots

### Anti-Detection
- Browser fingerprint randomization
- Human-like behavior simulation
- Request header modification
- Cloudflare protection bypass

### Data Management
- JSON file storage
- Timestamped screenshots
- Detailed logging
- Error handling and recovery

## Logging

The bot maintains detailed logs in the `supreme_logs` directory:
- Product discoveries
- Variant updates
- Error messages
- Performance statistics

## Error Handling

The bot includes comprehensive error handling:
- Connection retries
- Browser recovery
- Data backup
- Error logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for educational purposes only. Please use responsibly and in accordance with Supreme's terms of service.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- Playwright team for the excellent browser automation framework
- Supreme for providing the platform
- Contributors and users of this project 