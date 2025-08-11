#!/usr/bin/env python3
"""
Arquivo de entrada para produção no Render.com
"""
import os
import sys

# Adiciona o diretório src ao path para importações
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app

if __name__ == '__main__':
    #  Para desenvolvimento local
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
else:
    #  Para produção (Render.com usa Gunicorn)
    application = app
