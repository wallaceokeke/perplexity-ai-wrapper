"""
Perplexity AI Wrapper - Network Inspector
File: tools/network_inspector.py

This tool helps discover and document Perplexity's API endpoints
by monitoring network traffic during browser usage.
"""
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from pathlib import Path


class NetworkInspector:
    """
    Monitor and capture network requests to discover API structure
    """
    
    def __init__(self, output_dir: str = "api_discovery"):
        """
        Initialize network inspector
        
        Args:
            output_dir: Directory to save captured data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.captured_requests: List[Dict] = []
        self.captured_responses: List[Dict] = []
        self.api_endpoints: Dict[str, List[Dict]] = {}
        
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    async def start(self, headless: bool = False):
        """Start browser with network monitoring"""
        print("Starting Network Inspector...")
        print("="*70)
        
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        self.page = await self.context.new_page()
        
        # Set up network monitoring
        self.page.on("request", self._on_request)
        self.page.on("response", self._on_response)
        
        print("✓ Browser started with network monitoring")
        print("✓ Navigating to Perplexity...")
        
        await self.page.goto("https://www.perplexity.ai")
        await asyncio.sleep(2)
        
        print("✓ Ready to capture traffic\n")
    
    def _on_request(self, request):
        """Capture outgoing requests"""
        url = request.url
        
        # Only capture Perplexity API calls
        if 'perplexity.ai' in url and ('/api/' in url or '/socket' in url):
            request_data = {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'method': request.method,
                'headers': dict(request.headers),
                'post_data': request.post_data if request.method == 'POST' else None,
                'resource_type': request.resource_type
            }
            
            self.captured_requests.append(request_data)
            
            # Organize by endpoint
            endpoint = self._extract_endpoint(url)
            if endpoint not in self.api_endpoints:
                self.api_endpoints[endpoint] = []
            self.api_endpoints[endpoint].append(request_data)
            
            print(f"📤 REQUEST: {request.method} {endpoint}")
            if request.post_data:
                try:
                    payload = json.loads(request.post_data)
                    print(f"   Payload: {json.dumps(payload, indent=2)[:200]}...")
                except:
                    print(f"   Payload: {request.post_data[:100]}...")
    
    async def _on_response(self, response):
        """Capture incoming responses"""
        url = response.url
        
        # Only capture Perplexity API responses
        if 'perplexity.ai' in url and ('/api/' in url or '/socket' in url):
            try:
                body = await response.body()
                body_text = body.decode('utf-8')
                
                # Try to parse as JSON
                try:
                    body_json = json.loads(body_text)
                except:
                    body_json = None
                
                response_data = {
                    'timestamp': datetime.now().isoformat(),
                    'url': url,
                    'status': response.status,
                    'headers': dict(response.headers),
                    'body': body_json if body_json else body_text[:1000],
                    'content_type': response.headers.get('content-type', '')
                }
                
                self.captured_responses.append(response_data)
                
                endpoint = self._extract_endpoint(url)
                print(f"📥 RESPONSE: {response.status} {endpoint}")
                if body_json:
                    print(f"   Body: {json.dumps(body_json, indent=2)[:200]}...")
                
            except Exception as e:
                print(f"   Error capturing response: {str(e)}")
    
    def _extract_endpoint(self, url: str) -> str:
        """Extract endpoint from full URL"""
        # Remove base URL and query parameters
        if 'perplexity.ai' in url:
            parts = url.split('perplexity.ai')
            if len(parts) > 1:
                endpoint = parts[1].split('?')[0]
                return endpoint
        return url
    
    async def interactive_capture(self):
        """
        Interactive mode - user performs actions while we capture
        """
        print("\n" + "="*70)
        print("INTERACTIVE CAPTURE MODE")
        print("="*70)
        print("Instructions:")
        print("  1. Use the browser window to interact with Perplexity")
        print("  2. Perform searches, follow-ups, etc.")
        print("  3. All network traffic will be captured")
        print("  4. Press Ctrl+C in terminal when done")
        print("="*70 + "\n")
        
        try:
            # Keep running while user interacts
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n\nCapture stopped by user")
    
    async def automated_capture(self, queries: List[str]):
        """
        Automated capture - perform searches automatically
        
        Args:
            queries: List of search queries to test
        """
        print("\n" + "="*70)
        print("AUTOMATED CAPTURE MODE")
        print("="*70)
        print(f"Testing {len(queries)} queries...\n")
        
        for idx, query in enumerate(queries, 1):
            print(f"\n[{idx}/{len(queries)}] Testing query: {query}")
            print("-"*70)
            
            # Find search box
            search_box = await self.page.wait_for_selector(
                'textarea[placeholder*="Ask"]',
                timeout=10000
            )
            
            # Clear and type query
            await search_box.fill("")
            await search_box.type(query, delay=50)
            await search_box.press('Enter')
            
            # Wait for response
            print("Waiting for response...")
            await asyncio.sleep(5)  # Let response complete
            
            print(f"✓ Completed query {idx}")
            await asyncio.sleep(2)  # Delay between queries
    
    def analyze_endpoints(self) -> Dict[str, Any]:
        """
        Analyze captured traffic and generate endpoint documentation
        
        Returns:
            Analysis summary
        """
        print("\n" + "="*70)
        print("ENDPOINT ANALYSIS")
        print("="*70)
        
        analysis = {
            'total_requests': len(self.captured_requests),
            'total_responses': len(self.captured_responses),
            'unique_endpoints': len(self.api_endpoints),
            'endpoints': {}
        }
        
        # Analyze each endpoint
        for endpoint, requests in self.api_endpoints.items():
            methods = set(req['method'] for req in requests)
            
            # Sample payload
            sample_payload = None
            for req in requests:
                if req['post_data']:
                    try:
                        sample_payload = json.loads(req['post_data'])
                        break
                    except:
                        pass
            
            analysis['endpoints'][endpoint] = {
                'methods': list(methods),
                'call_count': len(requests),
                'sample_payload': sample_payload,
                'sample_request': requests[0] if requests else None
            }
            
            print(f"\nEndpoint: {endpoint}")
            print(f"  Methods: {', '.join(methods)}")
            print(f"  Calls: {len(requests)}")
            if sample_payload:
                print(f"  Sample Payload:")
                print(f"    {json.dumps(sample_payload, indent=4)[:300]}...")
        
        return analysis
    
    def save_results(self):
        """Save all captured data to files"""
        print("\n" + "="*70)
        print("SAVING RESULTS")
        print("="*70)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save requests
        requests_file = self.output_dir / f"requests_{timestamp}.json"
        with open(requests_file, 'w') as f:
            json.dump(self.captured_requests, f, indent=2)
        print(f"✓ Saved {len(self.captured_requests)} requests: {requests_file}")
        
        # Save responses
        responses_file = self.output_dir / f"responses_{timestamp}.json"
        with open(responses_file, 'w') as f:
            json.dump(self.captured_responses, f, indent=2)
        print(f"✓ Saved {len(self.captured_responses)} responses: {responses_file}")
        
        # Save endpoint analysis
        analysis = self.analyze_endpoints()
        analysis_file = self.output_dir / f"analysis_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"✓ Saved analysis: {analysis_file}")
        
        # Save endpoint documentation (Markdown)
        doc_file = self.output_dir / f"api_documentation_{timestamp}.md"
        self._generate_markdown_docs(doc_file, analysis)
        print(f"✓ Saved documentation: {doc_file}")
        
        print(f"\n✓ All results saved to: {self.output_dir}")
    
    def _generate_markdown_docs(self, filepath: Path, analysis: Dict):
        """Generate markdown documentation from analysis"""
        with open(filepath, 'w') as f:
            f.write("# Perplexity API Documentation\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Summary\n\n")
            f.write(f"- Total Requests: {analysis['total_requests']}\n")
            f.write(f"- Total Responses: {analysis['total_responses']}\n")
            f.write(f"- Unique Endpoints: {analysis['unique_endpoints']}\n\n")
            
            f.write("## Endpoints\n\n")
            
            for endpoint, data in analysis['endpoints'].items():
                f.write(f"### {endpoint}\n\n")
                f.write(f"**Methods:** {', '.join(data['methods'])}\n\n")
                f.write(f"**Call Count:** {data['call_count']}\n\n")
                
                if data['sample_payload']:
                    f.write("**Sample Payload:**\n\n")
                    f.write("```json\n")
                    f.write(json.dumps(data['sample_payload'], indent=2))
                    f.write("\n```\n\n")
                
                if data['sample_request']:
                    f.write("**Sample Request Headers:**\n\n")
                    f.write("```json\n")
                    headers = {k: v for k, v in data['sample_request']['headers'].items() 
                              if k.lower() not in ['cookie', 'authorization']}
                    f.write(json.dumps(headers, indent=2))
                    f.write("\n```\n\n")
                
                f.write("---\n\n")
    
    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("\n✓ Browser closed")


# ============================================================================
# CLI Interface
# ============================================================================

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Perplexity API Network Inspector"
    )
    parser.add_argument(
        '--mode',
        choices=['interactive', 'automated'],
        default='interactive',
        help='Capture mode'
    )
    parser.add_argument(
        '--queries',
        nargs='+',
        help='Queries for automated mode'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    parser.add_argument(
        '--output',
        default='api_discovery',
        help='Output directory'
    )
    
    args = parser.parse_args()
    
    # Initialize inspector
    inspector = NetworkInspector(output_dir=args.output)
    
    try:
        # Start browser
        await inspector.start(headless=args.headless)
        
        # Run capture
        if args.mode == 'interactive':
            await inspector.interactive_capture()
        else:
            queries = args.queries or [
                "What is artificial intelligence?",
                "Explain quantum computing",
                "Latest AI developments"
            ]
            await inspector.automated_capture(queries)
        
        # Save results
        inspector.save_results()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await inspector.close()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         Perplexity AI - Network Inspector Tool              ║
    ║                                                              ║
    ║  This tool captures API traffic to help understand the       ║
    ║  Perplexity.ai API structure and build accurate wrappers    ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())