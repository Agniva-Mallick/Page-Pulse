from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import httpx
import time
from urllib.parse import urlparse

app = FastAPI(title="Page Pulse API")

# Allow CORS for local development and general public access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def parse_html_content(html_content: str) -> dict:
    """
    Parses HTML content to extract SEO and content metrics.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 1. Page Title
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    
    # 2. Meta Description
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else None
    
    # 3. H1 Count
    h1_count = len(soup.find_all("h1"))
    
    # 4. Images missing alt text
    images = soup.find_all("img")
    images_missing_alt = sum(1 for img in images if not img.get("alt") or not img.get("alt").strip())
    
    # 5. Approximate word count
    # Remove script and style elements before counting words
    for script_or_style in soup(["script", "style", "noscript"]):
        script_or_style.decompose()
        
    text = soup.get_text(separator=' ')
    words = text.split()
    word_count = len(words)
    
    return {
        "page_title": title,
        "meta_description": meta_description,
        "h1_count": h1_count,
        "images_missing_alt": images_missing_alt,
        "approximate_word_count": word_count
    }

@app.get("/api/audit")
async def audit_url(url: str = Query(..., description="The URL to audit")):
    """
    Audits a given URL and returns JSON report.
    """
    # URL Validation
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        # Try to gracefully prepend https:// if missing
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise HTTPException(status_code=400, detail="Invalid URL format. Please provide a valid URL like 'https://example.com'.")
                
    if parsed.scheme not in ["http", "https"]:
        raise HTTPException(status_code=400, detail="Invalid URL scheme. Only http and https are supported.")

    start_time = time.time()
    
    try:
        # Fetch the URL
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            # We use a standard user agent to avoid being blocked by simple anti-bot filters
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            response = await client.get(url, headers=headers)
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Check for non-HTML content type
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type.lower():
                # We return a 200 with an error object rather than a 4xx so the frontend can display it nicely
                return {
                    "success": False,
                    "error_message": f"URL returned non-HTML content ({content_type.split(';')[0] if content_type else 'Unknown'}). This tool only audits HTML pages.",
                    "status_code": response.status_code,
                    "url": str(response.url)
                }
            
            # Parse the HTML content
            audit_data = parse_html_content(response.text)
            
            return {
                "success": True,
                "url": str(response.url), 
                "status_code": response.status_code,
                "response_time_ms": response_time_ms,
                "data": audit_data
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request timed out. The server took too long to respond.")
    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail="Failed to fetch the URL. Ensure the site is reachable and the URL is correct.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected internal error occurred during the audit.")

# Expose app for Vercel
# Vercel's Python runtime will look for the 'app' variable by default.
