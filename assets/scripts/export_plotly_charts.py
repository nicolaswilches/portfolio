#!/usr/bin/env python3
"""
Export Plotly charts from the Solar PV notebook as standalone HTML files.
Each chart is saved as a minimal HTML file that can be embedded via iframe.
"""

import json
import os
from pathlib import Path

# Paths
NOTEBOOK_PATH = Path(__file__).parent.parent / "notebooks" / "solar-pv-spain-forecast.ipynb"
OUTPUT_DIR = Path(__file__).parent.parent / "plots"

# Chart configurations - maps cell output to filename and description
CHARTS = [
    {"line": 2563, "name": "metrics_evaluation", "desc": "Metrics Evaluation: Energy Sold, Capacity Installed, Installations"},
    {"line": 8657, "name": "technologies_comparison", "desc": "Energy Sold by Technology Type"},
    {"line": 11965, "name": "decomposition", "desc": "Time Series Decomposition"},
    {"line": 14256, "name": "acf_pacf", "desc": "ACF and PACF Analysis"},
    {"line": 17359, "name": "transformations", "desc": "Solar PV Transformation & Differencing"},
    {"line": 18762, "name": "model_selection_acf", "desc": "ACF/PACF of Transformed Series for Model Selection"},
    {"line": 20450, "name": "residuals_diagnostic", "desc": "Residuals Diagnostic"},
    {"line": 21872, "name": "forecast_full", "desc": "Solar Photovoltaic vs. Fitted and Forecast (Full)"},
    {"line": 23219, "name": "forecast_trimmed", "desc": "Solar Photovoltaic vs. Fitted and Forecast (Trimmed)"},
]


def extract_plotly_from_notebook(notebook_path: Path) -> dict:
    """Load notebook and extract cells with Plotly outputs."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    cells_with_plotly = []
    
    for cell in notebook.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue
        
        outputs = cell.get('outputs', [])
        for output in outputs:
            if output.get('output_type') == 'display_data':
                data = output.get('data', {})
                if 'application/vnd.plotly.v1+json' in data:
                    plotly_data = data['application/vnd.plotly.v1+json']
                    source = ''.join(cell.get('source', []))
                    cells_with_plotly.append({
                        'source': source,
                        'plotly': plotly_data
                    })
    
    return cells_with_plotly


def create_html_chart(plotly_json: dict, title: str = "") -> str:
    """Create a minimal standalone HTML file for a Plotly chart."""
    # Update layout for better embedding
    if 'layout' in plotly_json:
        plotly_json['layout']['autosize'] = True
        plotly_json['layout']['margin'] = {'l': 50, 'r': 30, 't': 80, 'b': 50}
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ width: 100%; height: 100%; overflow: hidden; }}
        #chart {{ width: 100%; height: 100%; }}
    </style>
</head>
<body>
    <div id="chart"></div>
    <script>
        var figure = {json.dumps(plotly_json)};
        var config = {{
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            displaylogo: false
        }};
        Plotly.newPlot('chart', figure.data, figure.layout, config);
    </script>
</body>
</html>'''
    return html


def main():
    """Extract and save all Plotly charts from the notebook."""
    print(f"Reading notebook: {NOTEBOOK_PATH}")
    
    if not NOTEBOOK_PATH.exists():
        print(f"Error: Notebook not found at {NOTEBOOK_PATH}")
        return
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Extract all Plotly charts
    cells = extract_plotly_from_notebook(NOTEBOOK_PATH)
    print(f"Found {len(cells)} cells with Plotly outputs")
    
    # Save each chart
    for i, cell in enumerate(cells):
        # Determine filename based on chart content or index
        if i < len(CHARTS):
            filename = CHARTS[i]['name']
            desc = CHARTS[i]['desc']
        else:
            filename = f"chart_{i+1}"
            desc = f"Chart {i+1}"
        
        output_path = OUTPUT_DIR / f"{filename}.html"
        html = create_html_chart(cell['plotly'], desc)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  Saved: {output_path.name}")
    
    print(f"\nAll charts saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
