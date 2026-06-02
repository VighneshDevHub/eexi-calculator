# EEXI Calculator

Web-based Energy Efficiency Existing Ship Index (EEXI) calculator.
IMO Resolution MEPC.350(78) compliant.

## Quick Start

```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

## Run Tests

```bash
pytest tests/ -v --cov=eexi --cov-report=term-missing
```

## Deploy to Render

1. Push to GitHub
2. Connect repo on render.com
3. Render auto-detects `render.yaml` and deploys

## Project Structure

```
eexi_project/
├── app.py                  # Flask application
├── requirements.txt
├── render.yaml             # Render deployment config
├── eexi/
│   ├── __init__.py
│   ├── ship_params.py      # Reference line params + CF_MAP
│   ├── emissions.py        # PME, ME/AE emission terms
│   ├── eexi.py             # Attained/required EEXI + compliance
│   ├── epl.py              # EPL / ShaPoLi power limit
│   └── calculator.py       # Full pipeline (called by API)
├── tests/
│   ├── test_ship_params.py
│   ├── test_emissions.py
│   ├── test_eexi.py
│   ├── test_epl.py
│   └── test_calculator.py
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## References

- IMO Resolution MEPC.350(78)
- MARPOL Annex VI, Regulation 21
- IMO MEPC.1/Circ.896
