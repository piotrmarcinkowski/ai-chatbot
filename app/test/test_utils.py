from app.src.deep_research.utils import html_to_markdown

def test_html_to_markdown():
    """Test the html_to_markdown function."""
    html = """
    <html>
        <head><title>Test title</title></head>
        <body>
            <h1>Header</h1>
            <p>This is a <strong>test</strong> paragraph.</p>
            <a href="https://example.com">Example Link</a>
            <script>alert('Hi');</script>
            <style>body { font-size: 12px; }</style>
        </body>
    </html>
    """
    #expected_markdown = "# Test\n\n## Main Title\n\nThis is a **test** paragraph.\n\nExample Link\n"
    
    markdown = html_to_markdown(html)
    
    assert "Title: Test title" in markdown
    assert "# Header" in markdown
    assert "This is a **test** paragraph." in markdown
    assert "[Example Link](https://example.com)" in markdown
    assert "<script>" not in markdown
    assert "alert" not in markdown
    assert "<style>" not in markdown
    #assert markdown == expected_markdown

