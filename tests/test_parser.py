import pytest
import sys
import os

# Add the parent directory to sys.path so we can import the api package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.index import parse_html_content

def test_parse_html_happy_path():
    """
    Test the happy path where all expected HTML elements are present.
    """
    html = """
    <html>
        <head>
            <title>Happy Path Title</title>
            <meta name="description" content="This is a happy path description.">
        </head>
        <body>
            <h1>Main Heading</h1>
            <h1>Sub Heading</h1>
            <p>This is some test content. It has eight words total.</p>
            <img src="img1.jpg" alt="Valid alt text">
            <img src="img2.jpg" alt="">
            <img src="img3.jpg">
        </body>
    </html>
    """
    
    result = parse_html_content(html)
    
    assert result["page_title"] == "Happy Path Title"
    assert result["meta_description"] == "This is a happy path description."
    assert result["h1_count"] == 2
    assert result["images_missing_alt"] == 2  # one empty alt, one missing alt
    
    # words: "Main Heading Sub Heading This is some test content. It has eight words total." -> 14 words
    assert result["approximate_word_count"] == 14

def test_parse_html_missing_elements():
    """
    Test failure case 1: The HTML is missing title, meta description, and H1 tags.
    """
    html = """
    <html>
        <head>
            <!-- Missing title and meta description -->
        </head>
        <body>
            <!-- Missing H1 -->
            <h2>Secondary Heading</h2>
            <p>Just some plain text.</p>
        </body>
    </html>
    """
    
    result = parse_html_content(html)
    
    assert result["page_title"] is None
    assert result["meta_description"] is None
    assert result["h1_count"] == 0
    assert result["images_missing_alt"] == 0
    
    # words: "Secondary Heading Just some plain text." -> 6 words
    assert result["approximate_word_count"] == 6

def test_parse_html_malformed_and_scripts():
    """
    Test failure case 2: Malformed HTML and checking that scripts/styles are ignored in word count.
    """
    html = """
    <html>
        <head>
            <title>  Messy Title   
            </title>
            <style>
                body { color: red; }
            </style>
        </head>
        <body>
            <script>
                console.log("This should not be counted as words.");
            </script>
            <div>
                <h1>Heading
            </div>
            <p>Actual words here.</p>
    """
    
    result = parse_html_content(html)
    
    assert result["page_title"] == "Messy Title"
    assert result["h1_count"] == 1
    
    # words: "Heading Actual words here." -> 4 words
    assert result["approximate_word_count"] == 4
