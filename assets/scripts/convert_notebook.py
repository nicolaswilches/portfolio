#!/usr/bin/env python3
"""
Convert Jupyter notebook to HTML without requiring nbconvert.
Creates a self-contained HTML file with all outputs preserved.
"""

import json
import html
import re
from pathlib import Path

NOTEBOOK_PATH = Path("/Users/nicolaswilches/MBDS/portfolio/assets/notebooks/solar-pv-spain-forecast.ipynb")
OUTPUT_PATH = Path("/Users/nicolaswilches/MBDS/portfolio/notebooks/solar-pv-spain-forecast.html")

def markdown_to_html(md_text):
    """Simple markdown to HTML conversion."""
    lines = md_text.split('\n')
    result = []
    in_list = False
    in_code = False
    code_buffer = []
    
    for line in lines:
        # Code blocks
        if line.startswith('```'):
            if in_code:
                result.append(f'<pre><code>{html.escape(chr(10).join(code_buffer))}</code></pre>')
                code_buffer = []
                in_code = False
            else:
                in_code = True
            continue
        
        if in_code:
            code_buffer.append(line)
            continue
        
        # Horizontal rules
        if line.strip() in ['---', '___', '***']:
            result.append('<hr>')
            continue
        
        # Headings
        if line.startswith('#'):
            level = len(re.match(r'^#+', line).group())
            text = line[level:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            result.append(f'<h{level}>{text}</h{level}>')
            continue
        
        # Bold and italic
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
        
        # Links
        line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', line)
        
        # Lists
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(f'<li>{line.strip()[2:]}</li>')
            continue
        elif in_list and line.strip():
            result.append('</ul>')
            in_list = False
        
        # Paragraphs
        if line.strip():
            result.append(f'<p>{line}</p>')
        elif not in_list:
            result.append('')
    
    if in_list:
        result.append('</ul>')
    
    return '\n'.join(result)


def convert_notebook_to_html(notebook_path: Path, output_path: Path):
    """Convert notebook to standalone HTML."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    cells_html = []
    
    for cell in notebook.get('cells', []):
        cell_type = cell.get('cell_type', '')
        source = ''.join(cell.get('source', []))
        
        if cell_type == 'markdown':
            cells_html.append(f'<div class="cell markdown-cell">{markdown_to_html(source)}</div>')
        
        elif cell_type == 'code':
            # Code input
            code_html = f'<div class="input"><pre><code class="python">{html.escape(source)}</code></pre></div>'
            
            # Outputs
            outputs_html = []
            for output in cell.get('outputs', []):
                output_type = output.get('output_type', '')
                
                if output_type == 'stream':
                    text = ''.join(output.get('text', []))
                    outputs_html.append(f'<pre class="output-stream">{html.escape(text)}</pre>')
                
                elif output_type in ['execute_result', 'display_data']:
                    data = output.get('data', {})
                    
                    # Plotly
                    if 'application/vnd.plotly.v1+json' in data:
                        plotly_data = data['application/vnd.plotly.v1+json']
                        chart_id = f"plotly-{id(output)}"
                        outputs_html.append(f'''
                            <div id="{chart_id}" class="plotly-chart"></div>
                            <script>
                                (function() {{
                                    var data = {json.dumps(plotly_data)};
                                    Plotly.newPlot("{chart_id}", data.data, data.layout, {{responsive: true, displaylogo: false}});
                                }})();
                            </script>
                        ''')
                    
                    # HTML tables
                    elif 'text/html' in data:
                        html_content = ''.join(data['text/html'])
                        outputs_html.append(f'<div class="output-html">{html_content}</div>')
                    
                    # Plain text
                    elif 'text/plain' in data:
                        text = ''.join(data['text/plain'])
                        outputs_html.append(f'<pre class="output-text">{html.escape(text)}</pre>')
                
                elif output_type == 'error':
                    traceback = '\n'.join(output.get('traceback', []))
                    # Remove ANSI escape codes
                    traceback = re.sub(r'\x1b\[[0-9;]*m', '', traceback)
                    outputs_html.append(f'<pre class="output-error">{html.escape(traceback)}</pre>')
            
            outputs_section = f'<div class="outputs">{"".join(outputs_html)}</div>' if outputs_html else ''
            cells_html.append(f'<div class="cell code-cell">{code_html}{outputs_section}</div>')
    
    # Complete HTML document
    html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Solar Photovoltaic Generation in Spain: Time Series Modeling and Forecast</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root {{
            --bg: #ffffff;
            --bg-code: #f6f8fa;
            --text: #24292f;
            --border: #d0d7de;
            --primary: #ff6a00;
        }}
        
        * {{ box-sizing: border-box; }}
        
        body {{
            font-family: "Helvetica Neue", Helvetica, -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 16px;
            line-height: 1.6;
            color: var(--text);
            background: var(--bg);
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-weight: 600;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        
        h1 {{ font-size: 2rem; }}
        h2 {{ font-size: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3em; }}
        h3 {{ font-size: 1.25rem; }}
        
        .cell {{
            margin: 1.5rem 0;
        }}
        
        .input pre {{
            background: var(--bg-code);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 1rem;
            overflow-x: auto;
            font-family: "SF Mono", Consolas, monospace;
            font-size: 0.875rem;
        }}
        
        .outputs {{
            margin-top: 0.5rem;
        }}
        
        .output-stream, .output-text {{
            background: var(--bg-code);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 0.75rem;
            font-family: "SF Mono", Consolas, monospace;
            font-size: 0.875rem;
            overflow-x: auto;
        }}
        
        .output-error {{
            background: #ffebe9;
            border: 1px solid #ff8182;
            border-radius: 6px;
            padding: 0.75rem;
            font-family: monospace;
            font-size: 0.875rem;
            color: #cf222e;
        }}
        
        .output-html {{
            overflow-x: auto;
        }}
        
        .output-html table {{
            border-collapse: collapse;
            margin: 0.5rem 0;
            font-size: 0.875rem;
        }}
        
        .output-html th, .output-html td {{
            border: 1px solid var(--border);
            padding: 0.5rem;
            text-align: left;
        }}
        
        .output-html th {{
            background: var(--bg-code);
        }}
        
        .plotly-chart {{
            margin: 1rem 0;
        }}
        
        a {{
            color: var(--primary);
        }}
        
        hr {{
            border: none;
            height: 1px;
            background: var(--border);
            margin: 2rem 0;
        }}
        
        blockquote {{
            border-left: 4px solid var(--primary);
            padding-left: 1rem;
            margin-left: 0;
            color: #57606a;
        }}
        
        code {{
            background: var(--bg-code);
            padding: 0.15em 0.3em;
            border-radius: 3px;
            font-family: "SF Mono", Consolas, monospace;
            font-size: 0.875em;
        }}
        
        pre code {{
            padding: 0;
            background: none;
        }}
        
        .back-link {{
            display: inline-block;
            margin-bottom: 2rem;
            padding: 0.5rem 1rem;
            background: var(--bg-code);
            border-radius: 6px;
            text-decoration: none;
            color: var(--text);
        }}
        
        .back-link:hover {{
            background: var(--border);
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
                font-size: 15px;
            }}
        }}
    </style>
</head>
<body>
    <a href="../projects/solar-pv-spain-forecast" class="back-link">← Back to Case Study</a>
    
    <h1>Solar Photovoltaic Generation in Spain</h1>
    <p><em>Complete Jupyter Notebook with all code and interactive visualizations</em></p>
    <hr>
    
    {''.join(cells_html)}
    
    <hr>
    <p><a href="../projects/solar-pv-spain-forecast">← Back to Case Study</a></p>
</body>
</html>'''
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_doc)
    
    print(f"Converted notebook saved to: {output_path}")


if __name__ == "__main__":
    convert_notebook_to_html(NOTEBOOK_PATH, OUTPUT_PATH)
