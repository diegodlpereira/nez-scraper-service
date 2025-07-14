from flask import Flask, jsonify
import os
from datetime import datetime
from nez_scraper import ExtractorNezBistro, GeradorMarkdown

app = Flask(__name__)

@app.route('/scrape')
def scrape_nez():
    try:
        url = 'https://www.menudigital.app.br/nez/'
        extractor = ExtractorNezBistro(url)
        gerador = GeradorMarkdown(extractor)
        
        markdown_content = gerador.gerar_markdown_completo()
        
        return jsonify({
            "content": markdown_content,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e), 
            "status": "error"
        }), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "nez-scraper"})

@app.route('/')
def home():
    return jsonify({
        "message": "Nez Scraper Service", 
        "endpoints": ["/scrape", "/health"]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)