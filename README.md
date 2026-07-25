# Page Pulse

Page Pulse is a fast, robust URL auditing tool built for the Digital Heroes Software Development (SDE) task. It analyzes web pages and extracts key SEO and content metrics.

## Tech Stack
*   **Backend**: Python, FastAPI, httpx, BeautifulSoup4
*   **Frontend**: Vanilla HTML, CSS (Glassmorphism design), JavaScript
*   **Deployment**: Vercel (Serverless Functions for Python)

## Setup & Local Development

### Prerequisites
*   Python 3.9+
*   `pip`

### Installation
1.  Clone the repository.
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Start the FastAPI development server:
    ```bash
    uvicorn api.index:app --reload
    ```
4.  Open `public/index.html` in your browser. (The frontend is configured to automatically call `http://localhost:8000` when run locally).

### Running Tests
The parsing logic is fully tested using `pytest`.
```bash
pytest tests/
```

## API Contract

**Endpoint:** `GET /api/audit?url=<target_url>`

**Parameters:**
*   `url` (string, required): The fully qualified URL to audit (e.g., `https://example.com`).

**Successful Response (200 OK):**
```json
{
  "success": true,
  "url": "https://example.com",
  "status_code": 200,
  "response_time_ms": 145,
  "data": {
    "page_title": "Example Domain",
    "meta_description": null,
    "h1_count": 1,
    "images_missing_alt": 0,
    "approximate_word_count": 42
  }
}
```

**Graceful Error Response (200 OK) - e.g., Non-HTML Content:**
```json
{
  "success": false,
  "error_message": "URL returned non-HTML content (application/pdf). This tool only audits HTML pages.",
  "status_code": 200,
  "url": "https://example.com/file.pdf"
}
```

**Failure Response (4xx / 5xx):**
```json
{
  "detail": "Invalid URL scheme. Only http and https are supported."
}
```

## 3 Design Decisions

1.  **Separation of Fetching and Parsing (Testability)**
    *   **Decision**: I deliberately separated the network request logic (using `httpx`) from the HTML processing logic (`parse_html_content`).
    *   **Reasoning**: Network requests are slow and flaky. By extracting the pure parsing logic into a separate function, I was able to write fast, deterministic unit tests in `pytest` using hardcoded HTML strings, ensuring the parser handles edge cases (like missing tags or malformed HTML) without relying on live websites that might change or go down.

2.  **Graceful Handling of Non-HTML Content**
    *   **Decision**: Instead of letting BeautifulSoup crash or returning a generic 500 error when a user inputs a URL pointing to a PDF or an image, the backend explicitly checks the `Content-Type` header and returns a `success: false` JSON payload. 
    *   **Reasoning**: This provides a much better user experience. The frontend can read this payload and display a clean, friendly error message to the user ("This tool only audits HTML pages") instead of a cryptic server error.

3.  **Vanilla CSS with Glassmorphism over Heavy Frameworks**
    *   **Decision**: I opted to build the frontend using pure Vanilla HTML, CSS, and JS, utilizing CSS variables and modern layout techniques like CSS Grid, rather than reaching for React or Tailwind.
    *   **Reasoning**: For a simple single-page tool, pulling in a heavy frontend framework is overkill and increases load time. By writing custom CSS, I maintained total control over the aesthetics—specifically the premium glassmorphism effect and animations—keeping the bundle size practically zero while delivering a highly polished UI.

## AI Usage Statement

For this task, I used AI as an accelerator rather than a replacement for engineering judgment. I used it to quickly generate the Vercel serverless configuration (`vercel.json`) and to help scaffold the boilerplate HTML/CSS layout (the glassmorphism aesthetic). However, I manually engineered the core Python parsing logic with BeautifulSoup to ensure edge cases (like extracting scripts before counting words) were handled correctly. I also designed the API contract, wrote the specific unit test cases, and refined the JavaScript error handling myself to ensure the tool degrades gracefully in failure states. This approach allowed me to focus my time on application resilience and architecture rather than fighting CSS syntax.
