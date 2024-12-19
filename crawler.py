import sys
import json
import aiohttp
import asyncio
import re
import pandas as pd
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from urllib.parse import urljoin

async def domain_html_parser(session, domain, url_patterns, domain_urls, seen_urls):
    """Parse the HTML of a given domain and extract product URLs matching specified patterns."""
    try:
        async with session.get(domain, timeout=10) as response:
            if response.status != 200:
                print(f"Failed to fetch {domain}: HTTP {response.status}")
                return

            # Initialize the domain in the result map
            domain_urls[domain] = []
            html_txt_content = await response.text()
            html_content = BeautifulSoup(html_txt_content, 'html.parser')

            for link in html_content.find_all("a", href=True):
                url = str(urljoin(domain, link['href']))
                # checking if this url matches with given pattern or not
                if any(pattern.search(url) for pattern in url_patterns):
                    if url not in seen_urls:
                        seen_urls[url] = 1
                        domain_urls[domain].append(url)

    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"Error fetching {domain}: {e}")
    except Exception as e:
        print(f"Unexpected error on {domain}: {e}")

async def start_crawl(domains, url_patterns):
    """Start crawling all domains concurrently."""
    domain_urls = {}
    seen_urls = {}
    compiled_patterns = [re.compile(pattern) for pattern in url_patterns]

    async with aiohttp.ClientSession() as session:
        tasks = [
            domain_html_parser(session, domain, compiled_patterns, domain_urls, seen_urls)
            for domain in domains
        ]
        await asyncio.gather(*tasks)

    return domain_urls

def write_output_file(data):
    with open('output.txt', 'w') as file:
        file.write(json.dumps(data))

def load_domains(domains_file_path):
    """Load and parse domains from a file."""
    try:
        df = pd.read_csv(domains_file_path, header=None, names=['domains'], skip_blank_lines=True)
        return df['domains'].dropna().unique().tolist()
    except Exception as e:
        print(f"Error reading file {domains_file_path}: {e}")
        sys.exit(1)

def parse_arguments():
    """Parse command-line arguments."""
    parser = ArgumentParser(description="Web crawler for extracting matched patterns URLs from given list of e-commerce domains.")
    parser.add_argument(
        "file_path", type=str, help="Path to the file containing e-commerce domains (one domain per line)."
    )
    parser.add_argument(
        "patterns", type=str, help="Comma-separated list of regex patterns to match product URLs."
    )
    return parser.parse_args()

def main():
    """Main function to start the web crawler."""
    args = parse_arguments()

    # Split URL patterns into a list/array
    url_patterns = args.patterns.split(",")

    # Load domains from the provided file
    domains = load_domains(args.file_path)

    try:
        # Start the asynchronous crawl
        domain_urls = asyncio.run(start_crawl(domains, url_patterns))
        write_output_file(domain_urls)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
