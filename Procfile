web: gunicorn app:app --workers 2 --threads 4 --bind 0.0.0.0:$PORT --timeout 120
worker: python app.py
release: python app.py --setup
