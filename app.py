from flask import Flask, render_template
import pandas as pd
import json

app = Flask(__name__)

@app.route('/')
def index():
    df = pd.read_csv('data/Wireshark_TCP_HTTP_log.csv')
    # count how many times each IP appears in the dataset
    ip_counts = df['Source'].value_counts().reset_index()
    ip_counts.columns = ['IP', 'Count']
    # sort by count in descending order
    ip_counts = ip_counts.sort_values(by='Count', ascending=False)
    # get the top 10 IPs
    top_ips = ip_counts.head(10)
    # convert to HTML table
    top_ips_html = top_ips.to_html(classes='ip-table', index=False)
    # get the top IP (row with highest count)
    mal_ip = top_ips.iloc[0]
    # Round tile to nearest integer for grouping
    df['Time'] = df['Time'].round(0)
    # Group by time and source IP, count occurrences
    ping_counts = df.groupby(['Time', 'Source']).size().reset_index(name='Count')
    # Pivot for Chart.js: rows=Time, columns=Source, values=Count
    ping_counts_pivot = ping_counts.pivot(index='Time', columns='Source', values='Count')
    # Prepare data for Chart.js
    chart_labels = ping_counts_pivot.index.astype(str).tolist()
    chart_data = []
    for ip in ping_counts_pivot.columns:
        chart_data.append({
            'label': ip,
            'data': ping_counts_pivot[ip].fillna(0).tolist(),
            'borderColor': f'rgba({hash(ip) % 255}, {hash(ip) % 255}, {hash(ip) % 255}, 1)',
            'backgroundColor': f'rgba({hash(ip) % 255}, {hash(ip) % 255}, {hash(ip) % 255}, 0.2)',
        })
    return render_template(
        'index.html', 
        top_ips=top_ips_html, 
        top_ip=mal_ip['IP'], 
        top_ip_count=mal_ip['Count'],
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data)
    )

if __name__ == '__main__':
    app.run(debug=True)