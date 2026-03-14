"""
US Airline Market Analysis — Stakeholder Dashboard Generator
============================================================
Run this script from the same directory as your CSV file:

    python generate_dashboard.py

Output: airline_dashboard.html  (single self-contained file, opens in any browser)

Requirements:  pip install plotly pandas numpy
"""

import re
import os
import tempfile
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ── COLOR SYSTEM ───────────────────────────────────────────────────────────────
C_BASE  = '#4e8fc7'
C_LINE  = '#2166ac'
C_LIGHT = '#d0e4f3'
C_SEQ   = ['#c6dbef', '#6baed6', '#2171b5', '#08306b']
COMP_ORDER = ['Highly competitive', 'Moderate', 'Low competition', 'Near monopoly']
FONT = 'Inter, Arial, sans-serif'

# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════

print('Loading data...')

# Read the cleaned CSV produced by clean_data.py
if not __import__('os').path.exists('airline_cleaned.csv'):
    raise FileNotFoundError(
        'airline_cleaned.csv not found.\n'
        'Run clean_data.py first:  python clean_data.py'
    )

df = __import__('pandas').read_csv(
    'airline_cleaned.csv',
    dtype={'competition_level': 'category', 'load_band': 'category',
           'distance_band': 'category'},
)

# Restore ordered categoricals so groupby / reindex work correctly
import pandas as pd
COMP_ORDER_CAT = ['Highly competitive', 'Moderate', 'Low competition', 'Near monopoly']
BAND_ORDER_CAT = ['Very short', 'Short', 'Medium', 'Long', 'Very long']
LOAD_ORDER_CAT = ['<60%', '60-70%', '70-80%', '80-90%', '90-100%']

df['competition_level'] = pd.Categorical(df['competition_level'],
    categories=COMP_ORDER_CAT, ordered=True)
df['distance_band'] = pd.Categorical(df['distance_band'],
    categories=BAND_ORDER_CAT, ordered=True)
df['load_band'] = pd.Categorical(df['load_band'],
    categories=LOAD_ORDER_CAT, ordered=True)

print(f'Data ready: {df.shape[0]:,} rows x {df.shape[1]} columns')


# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT HELPER
# ══════════════════════════════════════════════════════════════════════════════

def style(fig, title, xtitle='', ytitle='', height=480):
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, family=FONT, color='#1a1a2e'), x=0.03),
        xaxis_title=xtitle, yaxis_title=ytitle,
        font=dict(family=FONT, size=12),
        template='plotly_white', height=height, autosize=True,
        margin=dict(l=70, r=40, t=75, b=60),
        hoverlabel=dict(bgcolor='white', font_size=12, font_family=FONT),
        legend=dict(bgcolor='rgba(255,255,255,0.9)', bordercolor='#dddddd', borderwidth=1),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# FIGURES  —  all data passed as plain Python lists (.tolist())
# ══════════════════════════════════════════════════════════════════════════════

print('Building charts...')


# ── KPI card values (computed from cleaned data) ──────────────────────────────
kpi_total_obs    = f"{len(df):,}"
kpi_avg_fare     = f"${df['average_fare'].mean():.0f}"
kpi_years        = f"{int(df['year'].min())}–{int(df['year'].max())}"
kpi_monopoly_pct = f"{(df['competition_level'] == 'Near monopoly').sum() / df['competition_level'].notna().sum() * 100:.0f}%"
kpi_postcovid    = f"${df[df['year'] >= 2022]['average_fare'].mean():.0f}"
kpi_cards_data   = [
    ('245,955',          'Route-Quarter Observations', 'Full dataset scope'),
    (kpi_avg_fare,       '31-Year Average Fare',       '1993–2024 mean'),
    (kpi_years,          'Analysis Period',            'Q1 1993 – Q4 2024'),
    (kpi_monopoly_pct,   'Near-Monopoly Routes',       'Dominant market structure'),
    (kpi_postcovid,      'Post-COVID Avg Fare',        '2022–2024 · highest era'),
]

# ── BQ-1: dropdown slicer by distance band ────────────────────────────────────
# Shows whether the competition→fare premium holds within each distance band.
# Each dropdown option swaps to a pre-computed trace for that band.

band_order  = ['Very short', 'Short', 'Medium', 'Long', 'Very long']
traces_fig1 = []
visibility_sets = []

# "All routes" trace
all_means = (df.groupby('competition_level', observed=True)['fare_per_mile']
             .mean().reindex(COMP_ORDER))
traces_fig1.append(go.Bar(
    x=COMP_ORDER, y=all_means.tolist(),
    marker_color=C_SEQ, marker_line_color='white', marker_line_width=0.8,
    text=[f'${v:.3f}' for v in all_means.tolist()],
    textposition='outside',
    name='All Routes', visible=True,
    hovertemplate='%{x}<br>Fare/mile: $%{y:.4f}<extra></extra>',
))

# One trace per distance band
for band in band_order:
    sub = df[df['distance_band'] == band]
    means = (sub.groupby('competition_level', observed=True)['fare_per_mile']
             .mean().reindex(COMP_ORDER))
    traces_fig1.append(go.Bar(
        x=COMP_ORDER, y=means.tolist(),
        marker_color=C_SEQ, marker_line_color='white', marker_line_width=0.8,
        text=[f'${v:.3f}' if not (v != v) else 'n/a' for v in means.tolist()],
        textposition='outside',
        name=band, visible=False,
        hovertemplate='%{x}<br>Fare/mile: $%{y:.4f}<extra></extra>',
    ))

# Build visibility lists (only one trace visible at a time)
n1 = len(traces_fig1)
buttons_fig1 = []
labels = ['All Routes'] + band_order
for i, label in enumerate(labels):
    vis = [j == i for j in range(n1)]
    buttons_fig1.append(dict(
        label=label, method='update',
        args=[{'visible': vis},
              {'title.text': f'BQ-1 — Fare/Mile by Competition Level · Filter: {label}'}]
    ))

fig1 = go.Figure(data=traces_fig1)
fig1 = style(fig1, 'BQ-1 — Mean Fare per Mile by Competition Level',
             'Competition Level', 'Mean Fare per Mile (USD)', 500)
fig1.update_yaxes(tickprefix='$', range=[0, 0.55])
fig1.update_layout(
    showlegend=False,
    margin=dict(l=70, r=40, t=120, b=60),
    updatemenus=[dict(
        type='dropdown', direction='down',
        x=1.0, xanchor='right', y=1.22, yanchor='top',
        bgcolor='white', bordercolor='#d0e4f3', borderwidth=1,
        font=dict(size=12, family=FONT),
        buttons=buttons_fig1,
        active=0,
    )],
    annotations=[dict(
        text='<b>Filter by Distance Band:</b>', showarrow=False,
        x=1.0, xref='paper', y=1.30, yref='paper',
        xanchor='right', font=dict(size=11, family=FONT, color='#4a5568'),
    )],
)

# ── BQ-2: dropdown slicer by competition level ────────────────────────────────
# Drill into whether distance still predicts fares within each market structure.
# Each option shows fare distributions (box) filtered to that competition tier.

traces_fig2 = []
comp_labels  = ['All Routes'] + COMP_ORDER

for i, clabel in enumerate(comp_labels):
    sub = df if clabel == 'All Routes' else df[df['competition_level'] == clabel]
    for j, band in enumerate(band_order):
        vals = sub.loc[sub['distance_band'] == band, 'average_fare'].dropna().tolist()
        traces_fig2.append(go.Box(
            y=vals, name=band,
            marker_color=C_BASE, line_color=C_LINE, fillcolor=C_LIGHT,
            visible=(i == 0),
            hovertemplate=f'<b>{band}</b><br>Fare: $%{{y:,.0f}}<extra></extra>',
        ))

# Build buttons — each shows 5 box traces (one per band) for that competition filter
buttons_fig2 = []
n_bands = len(band_order)
for i, clabel in enumerate(comp_labels):
    vis = [j // n_bands == i for j in range(len(traces_fig2))]
    buttons_fig2.append(dict(
        label=clabel, method='update',
        args=[{'visible': vis},
              {'title.text': f'BQ-2 — Fare by Distance Band · Filter: {clabel}'}]
    ))

fig2 = go.Figure(data=traces_fig2)
fig2 = style(fig2, 'BQ-2 — Fare Distribution by Distance Band',
             'Distance Band', 'Average Fare (USD)', 510)
fig2.update_yaxes(tickprefix='$')
fig2.update_layout(
    showlegend=False,
    margin=dict(l=70, r=40, t=120, b=60),
    updatemenus=[dict(
        type='dropdown', direction='down',
        x=1.0, xanchor='right', y=1.22, yanchor='top',
        bgcolor='white', bordercolor='#d0e4f3', borderwidth=1,
        font=dict(size=12, family=FONT),
        buttons=buttons_fig2,
        active=0,
    )],
    annotations=[dict(
        text='<b>Filter by Competition Level:</b>', showarrow=False,
        x=1.0, xref='paper', y=1.30, yref='paper',
        xanchor='right', font=dict(size=11, family=FONT, color='#4a5568'),
    )],
)

# ── BQ-3: density contour — unchanged (no slicer needed) ─────────────────────
pax_cap  = float(df['passenger_count'].quantile(0.98))
fare_cap = float(df['average_fare'].quantile(0.98))
fig3 = go.Figure(go.Histogram2dContour(
    x=df['passenger_count'].clip(upper=pax_cap).tolist(),
    y=df['average_fare'].clip(upper=fare_cap).tolist(),
    colorscale='Blues', reversescale=False, showscale=True, ncontours=22,
    line=dict(width=0.5),
    colorbar=dict(title='Density', tickfont=dict(size=10)),
    hovertemplate='Passengers: %{x:,.0f}<br>Fare: $%{y:.0f}<extra></extra>',
))
fig3 = style(fig3, 'BQ-3 — Passenger Volume vs Average Fare (full 245k dataset)',
             'Quarterly Passenger Count', 'Average Fare (USD)', 490)
fig3.update_yaxes(tickprefix='$')

# ── BQ-4a: violin — unchanged ─────────────────────────────────────────────────
load_order = ['<60%', '60-70%', '70-80%', '80-90%', '90-100%']
fig4a = go.Figure()
for band in load_order:
    vals = df.loc[df['load_band'] == band, 'average_fare'].dropna().tolist()
    fig4a.add_trace(go.Violin(
        y=vals, name=band,
        box_visible=True, meanline_visible=False,
        fillcolor=C_LIGHT, line_color=C_LINE,
        marker=dict(color=C_BASE, size=2, opacity=0.3),
        points=False,
        hovertemplate=f'<b>{band}</b><br>Fare: $%{{y:,.0f}}<extra></extra>',
    ))
fig4a = style(fig4a, 'BQ-4 — Fare Distribution by Load Factor Band',
              'Load Factor Band', 'Average Fare (USD)', 470)
fig4a.update_yaxes(tickprefix='$')
fig4a.update_layout(showlegend=False)

# ── BQ-4b: correlation heatmap — unchanged ────────────────────────────────────
corr_cols = ['distance_miles', 'passenger_count', 'market_load_factor', 'average_fare']
corr = df[corr_cols].corr().round(2)
mask = np.zeros_like(corr.values, dtype=float)
mask[np.triu_indices_from(mask, k=1)] = np.nan
corr_masked = (corr.values + mask).tolist()
fig4b = go.Figure(go.Heatmap(
    z=corr_masked, x=corr_cols, y=corr_cols,
    colorscale='RdBu', zmid=0, zmin=-1, zmax=1,
    text=[[f'{v:.2f}' if not (isinstance(v, float) and v != v) else ''
           for v in row] for row in corr_masked],
    texttemplate='%{text}', textfont=dict(size=14, color='#1a1a2e'),
    hovertemplate='%{y} x %{x}<br>r = %{z:.2f}<extra></extra>',
    showscale=True, colorbar=dict(title='r', tickfont=dict(size=10)),
))
fig4b = style(fig4b, 'BQ-4 — Correlation Matrix: Key Variables', '', '', 420)
fig4b.update_layout(margin=dict(l=150, r=40, t=75, b=120))

# ── BQ-5: dropdown slicer by competition level + range slider ─────────────────
# Most powerful drill-down: reveals diverging fare trajectories between
# competitive and monopoly routes over 31 years.
# Range slider lets stakeholders zoom into any structural period.

comp_groups  = ['All Routes', 'Highly competitive', 'Moderate',
                'Low competition', 'Near monopoly']
comp_colors  = [C_LINE, '#c6dbef', '#6baed6', '#2171b5', '#08306b']
comp_fills   = ['rgba(78,143,199,0.06)', 'rgba(198,219,239,0.10)',
                'rgba(107,174,214,0.10)', 'rgba(33,113,181,0.10)',
                'rgba(8,48,107,0.10)']
comp_widths  = [2.5, 1.8, 1.8, 1.8, 1.8]

traces_fig5 = []
for i, grp in enumerate(comp_groups):
    if grp == 'All Routes':
        sub_trend = df.groupby('year')['average_fare'].mean().reset_index()
    else:
        sub_trend = (df[df['competition_level'] == grp]
                     .groupby('year')['average_fare'].mean().reset_index())
    yrs  = sub_trend['year'].tolist()
    frs  = sub_trend['average_fare'].tolist()

    # Area fill trace
    traces_fig5.append(go.Scatter(
        x=yrs, y=frs, fill='tozeroy',
        fillcolor=comp_fills[i],
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False, hoverinfo='skip',
        visible=(i == 0),
    ))
    # Line trace
    traces_fig5.append(go.Scatter(
        x=yrs, y=frs, name=grp,
        mode='lines+markers',
        line=dict(color=comp_colors[i], width=comp_widths[i]),
        marker=dict(size=5, color=comp_colors[i]),
        hovertemplate=f'<b>{grp}</b> · %{{x}}<br>Avg fare: $%{{y:.0f}}<extra></extra>',
        visible=(i == 0),
    ))

# Annotations for All Routes only (indices 0 & 1)
ann_base = []
fare_trend_all = df.groupby('year')['average_fare'].mean().reset_index()
yrs_all  = fare_trend_all['year'].tolist()
frs_all  = fare_trend_all['average_fare'].tolist()
for yr, label, ay in [(2001, '9/11', 70), (2008, '2008 Crisis', 70), (2020, 'COVID-19', -70)]:
    if yr in yrs_all:
        ann_base.append(dict(
            x=yr, y=frs_all[yrs_all.index(yr)], text=label,
            showarrow=True, arrowhead=2, arrowwidth=1.2, arrowcolor='#888',
            ay=ay, ax=0, font=dict(size=10, color='#333'),
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#ccc', borderwidth=1, borderpad=3,
        ))

# Dropdown buttons — each shows exactly 2 traces (fill + line) for that group
n5 = len(traces_fig5)
buttons_fig5 = []
for i, grp in enumerate(comp_groups):
    vis = [j // 2 == i for j in range(n5)]
    ann = ann_base if i == 0 else []
    buttons_fig5.append(dict(
        label=grp, method='update',
        args=[{'visible': vis},
              {'title.text': f'BQ-5 — Avg Fare Trend 1993–2024 · {grp}',
               'annotations': ann}]
    ))

fig5 = go.Figure(data=traces_fig5)
fig5.update_layout(annotations=ann_base)
fig5 = style(fig5, 'BQ-5 — Avg Fare Trend 1993–2024 · All Routes',
             'Year', 'Average Fare (USD)', 540)
fig5.update_yaxes(tickprefix='$', rangemode='tozero')
fig5.update_xaxes(
    dtick=2,
    rangeslider=dict(visible=True, thickness=0.06, bgcolor='#f0f7ff'),
    rangeselector=dict(
        buttons=[
            dict(count=8,  label='LCC Era',          step='year', stepmode='backward'),
            dict(count=14, label='Consolidation Era', step='year', stepmode='backward'),
            dict(step='all', label='Full 31 Years'),
        ],
        bgcolor='white', bordercolor='#d0e4f3', borderwidth=1,
        font=dict(size=11, family=FONT), activecolor='#2166ac',
        x=0.0, y=1.02,
    ),
)
fig5.update_layout(
    showlegend=False,
    margin=dict(l=70, r=40, t=120, b=60),
    updatemenus=[dict(
        type='dropdown', direction='down',
        x=1.0, xanchor='right', y=1.22, yanchor='top',
        bgcolor='white', bordercolor='#d0e4f3', borderwidth=1,
        font=dict(size=12, family=FONT),
        buttons=buttons_fig5,
        active=0,
    )],
    annotations=ann_base + [dict(
        text='<b>Filter by Competition Level:</b>', showarrow=False,
        x=1.0, xref='paper', y=1.30, yref='paper',
        xanchor='right', font=dict(size=11, family=FONT, color='#4a5568'),
    )],
)



# ══════════════════════════════════════════════════════════════════════════════
# EXTRACT HTML VIA write_html TEMP FILES
# ══════════════════════════════════════════════════════════════════════════════

print('Extracting chart HTML...')

import tempfile, os

def fig_to_embed(fig):
    """
    Write figure as a complete standalone HTML file, read it back,
    strip the outer html/head/body tags, keep everything inside <body>.
    This is the only method guaranteed to include both chart data AND
    the Plotly render call — we never touch the serialisation ourselves.
    """
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False,
                                     mode='w', encoding='utf-8') as fh:
        tmp = fh.name
    fig.write_html(tmp, full_html=True, include_plotlyjs=False,
                   config={'displayModeBar': True,
                           'modeBarButtonsToRemove': ['select2d','lasso2d','autoScale2d'],
                           'displaylogo': False, 'responsive': True})
    with open(tmp, encoding='utf-8') as fh:
        raw = fh.read()
    os.unlink(tmp)
    # Extract everything inside <body>...</body>
    body_start = raw.index('<body>') + len('<body>')
    body_end   = raw.index('</body>')
    return raw[body_start:body_end].strip()

div1  = fig_to_embed(fig1)
div2  = fig_to_embed(fig2)
div3  = fig_to_embed(fig3)
div4a = fig_to_embed(fig4a)
div4b = fig_to_embed(fig4b)
div5  = fig_to_embed(fig5)
print('All charts extracted.')

# Individual files
os.makedirs('charts', exist_ok=True)
for fname, fig in [
    ('charts/bq1_competition_fare.html',    fig1),
    ('charts/bq2_distance_fare.html',       fig2),
    ('charts/bq3_demand_density.html',      fig3),
    ('charts/bq4_loadfactor_violin.html',   fig4a),
    ('charts/bq4_correlation_heatmap.html', fig4b),
    ('charts/bq5_fare_trend.html',          fig5),
]:
    fig.write_html(fname, include_plotlyjs='cdn', full_html=True)
    print(f'  Written: {fname}')


# ══════════════════════════════════════════════════════════════════════════════
# ASSEMBLE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

sections = [
    {
        'id':'section-1','bq':'BQ-1',
        'title':'Market Concentration & Pricing Power',
        'question':'Does reduced competition directly translate to higher fares per mile — and by how much?',
        'divs':[div1],
        'interp':(
            '<ul>'
            '<li>Competitive routes average <strong>$0.16/mile</strong>; near-monopoly routes average <strong>$0.33/mile</strong> — a <strong>+106% premium</strong> for the same distance.</li>'
            '<li>The step is monotonic across all four tiers: $0.16 → $0.22 → $0.25 → $0.33.</li>'
            '<li>Medians confirm it is not outlier-driven: $0.14 → $0.18 → $0.20 → $0.25.</li>'
            '<li>Fare dispersion also widens: std dev jumps from <strong>$0.10 on competitive</strong> to <strong>$0.27 on near-monopoly</strong> routes.</li>'
            '<li><strong>79,490 route-quarters</strong> sit in the near-monopoly tier — the largest single category in the dataset.</li>'
            '</ul>'
        ),
        'insight':(
            '<ul>'
            '<li>The $0.17/mile gap equals <strong>~$170 extra per passenger on a 1,000-mile route</strong>.</li>'
            '<li>Distance, load factor, and volume are all weak predictors of fare; market structure is the only variable that explains the premium.</li>'
            '<li>A new entrant can price 20–25% below the incumbent and still cover costs — the structural premium makes room for it.</li>'
            '<li>Route-level HHI is a more useful regulatory metric than national carrier count.</li>'
            '</ul>'
        ),
    },
    {
        'id':'section-2','bq':'BQ-2',
        'title':'Economies of Distance in Airline Pricing',
        'question':'Does route distance explain pricing behavior, or do other forces dominate on long-haul?',
        'divs':[div2],
        'interp':(
            '<ul>'
            '<li>Mean fares rise 75% from shortest to longest: <strong>$172 (very short) → $193 → $218 → $269 → $302 (very long)</strong>.</li>'
            '<li>Coefficient of variation peaks at <strong>42.1% on very short routes</strong>, dips to 30.0% on long, then climbs back to 33.4% on very long — dispersion grows where market power dominates.</li>'
            '<li>Upper whiskers on Long and Very long extend well above $400, driven by transcontinental and Hawaii concentration, not distance alone.</li>'
            '</ul>'
        ),
        'insight':(
            '<ul>'
            '<li>Distance sets the cost <strong>floor</strong>; competition sets the <strong>ceiling</strong>.</li>'
            '<li>A short monopoly route can charge more per mile than a long competitive corridor.</li>'
            '<li>Pricing models need both distance (cost proxy) and route-level concentration (market ceiling) — not distance alone.</li>'
            '</ul>'
        ),
    },
    {
        'id':'section-3','bq':'BQ-3',
        'title':'Demand Distribution & Price Sensitivity',
        'question':'Does higher passenger volume discipline fare levels, or do airlines maintain pricing floors?',
        'divs':[div3],
        'interp':(
            '<ul>'
            '<li>Distribution is heavily right-skewed: <strong>median 113 passengers/quarter</strong>, mean 299 — a handful of corridors dominate total traffic.</li>'
            '<li>High-volume routes compress into a fare band of <strong>$150–$280</strong>; the ceiling falls but the floor does not.</li>'
            '<li>Even at peak volume, fares rarely drop below <strong>$100–$120</strong> — a structural floor volume cannot erode.</li>'
            '<li>Passenger–fare correlation is just <strong>−0.17</strong> — volume explains almost none of the cross-route fare variation.</li>'
            '</ul>'
        ),
        'insight':(
            '<ul>'
            '<li>Volume compresses the fare <strong>ceiling</strong> but cannot move the <strong>floor</strong>.</li>'
            '<li>Most routes (75% carry &lt;339 passengers/quarter) have low volume <em>and</em> low competitive pressure — a double pricing disadvantage for passengers.</li>'
            '<li>Only competitive entry, not traffic growth, consistently drives fares down.</li>'
            '</ul>'
        ),
    },
    {
        'id':'section-4','bq':'BQ-4',
        'title':'Capacity Utilization & Pricing Strategy',
        'question':'Is load factor a meaningful predictor of what passengers pay?',
        'divs':[div4a, div4b],
        'interp':(
            '<ul>'
            '<li>All five load bands (&lt;60% through &gt;90%) show <strong>near-identical fare distributions</strong> — medians stable at $200–$215 across every band.</li>'
            '<li>Load factor vs. fare correlation = <strong>−0.19</strong>: effectively zero, and negative.</li>'
            '<li>A flight at <strong>95% capacity charges the same as one at 55%</strong>.</li>'
            '<li>Distance (+0.50) is the only variable with meaningful fare correlation in the matrix.</li>'
            '</ul>'
        ),
        'insight':(
            '<ul>'
            '<li>Fares are locked in months before departure via booking curves — load factor is a <strong>lagging outcome</strong>, not a pricing driver.</li>'
            '<li>Forward-looking signals that matter: <strong>booking pace</strong>, <strong>competitor capacity changes</strong>, <strong>route-level concentration</strong>.</li>'
            '<li>Load factor belongs in capacity planning (fleet, frequency) — not in pricing models.</li>'
            '</ul>'
        ),
    },
    {
        'id':'section-5','bq':'BQ-5',
        'title':'Long-Run Fare Trend (1993–2024)',
        'question':'What does the 30-year fare trend reveal about structural pricing shifts?',
        'divs':[div5],
        'interp':(
            '<ul>'
            '<li><strong>Deregulation era (1993–2000):</strong> Fares flat at $212–$219, +2% over 8 years.</li>'
            '<li><strong>Post-9/11 trough (2001–2005):</strong> Fell $201 → $187 (−7%) as demand collapsed and LCC capacity expanded.</li>'
            '<li><strong>Consolidation rise (2005–2019):</strong> Climbed $187 → $241, a <strong>+29% increase</strong> aligned precisely with the four major mergers.</li>'
            '<li><strong>COVID collapse (2020–2021):</strong> Dropped to ~$194, recovered to $206 by 2021.</li>'
            '<li><strong>Post-COVID (2022–2024):</strong> <strong>$250–$257</strong> — the highest sustained level in 31 years, <strong>17% above the 2019 pre-COVID peak</strong>.</li>'
            '</ul>'
        ),
        'insight':(
            '<ul>'
            '<li>The +29% consolidation rise happened while CPI inflation averaged ~2% — <strong>real fares rose substantially</strong>.</li>'
            '<li>Post-COVID fares exceeding pre-COVID levels <strong>despite lower demand</strong> confirms the regime shift is structural, not cyclical.</li>'
            '<li>The lowest fares in 31 years were in 2004–2005 — at the peak of LCC competitive entry. Competition, not macroeconomics, is the dominant long-run fare lever.</li>'
            '</ul>'
        ),
    },
]
findings = [
    {
        'n':'01',
        'title':'Market Structure Is the Primary Driver of Fare Levels',
        'body':(
            '<strong>What the data shows:</strong> Near-monopoly routes charge <strong>$0.33/mile</strong> '
            'vs <strong>$0.16/mile</strong> on highly competitive routes — a <strong>+106% premium</strong> '
            'that is monotonic across all four competition tiers and holds across all 31 years and all '
            'distance bands. With 79,490 near-monopoly route-quarters in the dataset, concentrated pricing '
            'is not an edge case — it is the dominant structure of US domestic aviation.<br><br>'
            '<strong>Why it matters:</strong> The $0.17/mile gap translates to approximately $170 extra '
            'per passenger on a 1,000-mile route, and roughly $340 extra on a transcontinental segment. '
            'Fare differences between routes are not explained by distance, aircraft type, or load factor '
            '— all of which have near-zero or weak correlations with fare. The only variable that '
            'explains the premium is market share concentration.<br><br>'
            '<strong>What to do:</strong> For a network planner: target routes with dominant carrier '
            'share above 80% and quarterly passenger volumes above 100 — those passengers are '
            'paying a structural premium that a competitive entrant can undercut while maintaining '
            'positive unit economics. For a regulator: route-level HHI is a more informative '
            'metric than national carrier count when evaluating merger impacts.'
        ),
    },
    {
        'n':'02',
        'title':'Load Factor Is a Lagging Output, Not a Pricing Input',
        'body':(
            '<strong>What the data shows:</strong> The correlation between market load factor and average '
            'fare is <strong>−0.19</strong> across 245,955 observations. Violin distributions for '
            'all five load bands (&lt;60% through &gt;90%) are statistically near-identical, with '
            'medians stable at $200–$215 regardless of utilization. A flight running at 95% '
            'capacity charges the same fare as one at 55%.<br><br>'
            '<strong>Why it matters:</strong> Revenue management systems set fares months before '
            'departure using booking curve velocity. By the time load factor is observable, every '
            'meaningful pricing decision is already locked in. Any model that uses current-period '
            'load factor as a fare predictor is regressing on a lagging outcome, not a causal '
            'driver. Distance, by contrast, correlates at +0.50 with fare — a genuine '
            'cost-side baseline that belongs in pricing models.<br><br>'
            '<strong>What to do:</strong> Remove load factor from fare prediction models and replace '
            'it with forward-looking signals: booking pace (seats sold per day-to-departure), '
            'competitive schedule changes (capacity additions/withdrawals on the route), and '
            'historical price elasticity by segment. Reserve load factor for capacity planning: '
            'fleet sizing, frequency optimization, and gauge decisions.'
        ),
    },
    {
        'n':'03',
        'title':'Long-Run Fare Growth Is a Consolidation Effect, Not an Inflation Effect',
        'body':(
            '<strong>What the data shows:</strong> Average fares rose <strong>+29%</strong> during '
            'the consolidation era (2005–2019), from $187 to $241, compared to just +2% during '
            'the prior 8-year deregulation era ($212–$219). The post-COVID recovery (2022–2024) '
            'pushed fares to <strong>$250–$257</strong> — <strong>17% above the 2019 '
            'pre-COVID peak</strong> and the highest sustained level in 31 years.<br><br>'
            '<strong>Why it matters:</strong> The +29% consolidation-era increase occurred during a '
            'period when CPI inflation averaged ~2% annually, meaning real fares rose substantially. '
            'The timing aligns precisely with Delta/Northwest (2008), United/Continental (2010), '
            'Southwest/AirTran (2011), and American/US Airways (2013) — four mergers that '
            'reduced the major carrier count from ~10 to 4. The post-COVID fare level exceeding '
            'pre-COVID despite lower overall demand confirms the regime shift is structural, '
            'not cyclical.<br><br>'
            '<strong>What to do:</strong> For policy: merger review should use route-level fare '
            'impact modeling, not national capacity concentration metrics. For strategy: carriers '
            'planning hub entry should expect entrenched pricing power from incumbents and model '
            'a 12–24 month fare war before equilibrium. The data supports a price-disruption '
            'entry strategy over a matching-incumbent approach.'
        ),
    },
]


def S(s):
    charts = ''.join(f'<div class="chart-wrap">{d}</div>' for d in s['divs'])
    return f"""<section class="analysis-section" id="{s['id']}">
      <div class="section-header">
        <span class="bq-badge">{s['bq']}</span>
        <h2 class="section-title">{s['title']}</h2>
        <p class="section-question">{s['question']}</p>
      </div>
      {charts}
      <div class="insight-box">
        <div class="insight-row">
          <div class="insight-block"><span class="insight-label">Interpretation</span>{s['interp']}</div>
          <div class="insight-block insight-highlight"><span class="insight-label">Insight</span>{s['insight']}</div>
        </div>
      </div>
    </section>"""

def F(f):
    return f"""<div class="finding-card">
      <div class="finding-number">{f['n']}</div>
      <div class="finding-body"><h3 class="finding-title">{f['title']}</h3><p>{f['body']}</p></div>
    </div>"""

sections_html = '\n'.join(S(s) for s in sections)
findings_html = '\n'.join(F(f) for f in findings)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>US Airline Market Analysis 1993-2024 - Zakarias Musa</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bd:#1a1a2e;--bm:#2166ac;--bl:#d0e4f3;--bp:#f0f7ff;--tx:#1a1a2e;--tm:#4a5568;--br:#e2e8f0;--wh:#ffffff;--fn:'Inter','Segoe UI',Arial,sans-serif;--rad:10px;--sh:0 2px 14px rgba(33,102,172,.08)}}
body{{font-family:var(--fn);background:#f7fafd;color:var(--tx);line-height:1.65}}
.cover{{background:linear-gradient(135deg,#1a1a2e 0%,#2166ac 100%);color:#fff;padding:72px 48px 60px;position:relative;overflow:hidden}}
.cover::after{{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 70% 50%,rgba(255,255,255,.05) 0%,transparent 60%);pointer-events:none}}
.cover-meta{{font-size:11px;letter-spacing:.14em;text-transform:uppercase;opacity:.6;margin-bottom:16px}}
.cover h1{{font-size:clamp(22px,4vw,36px);font-weight:700;line-height:1.2;margin-bottom:10px}}
.cover-sub{{font-size:14px;opacity:.7;margin-bottom:40px;max-width:540px}}
.cover-stats{{display:flex;gap:32px;flex-wrap:wrap}}
.stat{{border-left:2px solid rgba(255,255,255,.25);padding-left:14px}}
.stat-value{{font-size:21px;font-weight:700;display:block}}
.stat-label{{font-size:10px;opacity:.55;text-transform:uppercase;letter-spacing:.09em}}
.nav{{background:#fff;border-bottom:1px solid var(--br);padding:0 48px;position:sticky;top:0;z-index:100;display:flex;gap:2px;overflow-x:auto}}
.nav a{{display:inline-block;padding:13px 15px;font-size:11.5px;font-weight:600;letter-spacing:.04em;color:var(--tm);text-decoration:none;border-bottom:2px solid transparent;white-space:nowrap;transition:color .15s,border-color .15s}}
.nav a:hover{{color:var(--bm);border-color:var(--bm)}}
.container{{max-width:1100px;margin:0 auto;padding:0 32px}}
.bq-overview{{background:#fff;border:1px solid var(--br);border-radius:var(--rad);padding:36px 40px;margin:48px 0 16px;box-shadow:var(--sh)}}
.bq-overview h2{{font-size:17px;margin-bottom:18px}}
.bq-table{{width:100%;border-collapse:collapse;font-size:13px}}
.bq-table th{{text-align:left;padding:8px 14px;background:var(--bp);color:var(--tm);font-size:10px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;border-bottom:1px solid var(--br)}}
.bq-table td{{padding:11px 14px;border-bottom:1px solid var(--br)}}
.bq-table tr:last-child td{{border-bottom:none}}
.bq-table tr:hover td{{background:var(--bp)}}
.bq-pill{{display:inline-block;background:var(--bm);color:#fff;font-size:9.5px;font-weight:700;padding:2px 8px;border-radius:20px;letter-spacing:.06em}}
.analysis-section{{background:#fff;border:1px solid var(--br);border-radius:var(--rad);margin:32px 0;box-shadow:var(--sh);overflow:hidden}}
.section-header{{padding:26px 36px 18px;border-bottom:1px solid var(--br);background:var(--bp)}}
.bq-badge{{display:inline-block;background:var(--bm);color:#fff;font-size:9.5px;font-weight:700;padding:2px 9px;border-radius:20px;letter-spacing:.08em;margin-bottom:7px}}
.section-title{{font-size:19px;font-weight:700;margin-bottom:5px}}
.section-question{{font-size:13px;color:var(--tm);font-style:italic;max-width:660px}}
.chart-wrap{{padding:22px 26px 6px}}
.chart-wrap .plotly-graph-div{{width:100%!important}}
.insight-box{{padding:18px 26px 26px;border-top:1px solid var(--br)}}
.insight-row{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media(max-width:680px){{.insight-row{{grid-template-columns:1fr}}}}
.insight-block{{padding:16px 18px;border-radius:8px;font-size:13px;background:var(--bp)}}
.insight-block.insight-highlight{{background:var(--bl);border-left:3px solid var(--bm)}}
.insight-label{{display:block;font-size:9.5px;font-weight:700;letter-spacing:.11em;text-transform:uppercase;color:var(--bm);margin-bottom:7px}}.insight-block ul{{margin:0;padding-left:18px;list-style:disc}}.insight-block ul li{{font-size:13px;line-height:1.65;margin-bottom:7px;padding-left:2px}}.insight-block ul li:last-child{{margin-bottom:0}}
.exec-summary{{background:var(--bd);color:#fff;border-radius:var(--rad);padding:48px 40px;margin:48px 0}}
.exec-summary h2{{font-size:22px;margin-bottom:4px}}
.exec-sub{{font-size:11px;opacity:.5;text-transform:uppercase;letter-spacing:.12em;margin-bottom:36px}}
.finding-card{{display:flex;gap:24px;padding:24px 0;border-bottom:1px solid rgba(255,255,255,.09)}}
.finding-card:last-child{{border-bottom:none}}
.finding-number{{font-size:34px;font-weight:800;color:var(--bl);opacity:.35;line-height:1;min-width:44px}}
.finding-title{{font-size:14.5px;font-weight:700;margin-bottom:8px}}
.finding-body{{font-size:13px;opacity:.78;line-height:1.7}}
.finding-body strong{{color:#fff;opacity:1}}
.kpi-row{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin:36px 0 20px}}@media(max-width:900px){{.kpi-row{{grid-template-columns:repeat(3,1fr)}}}}@media(max-width:600px){{.kpi-row{{grid-template-columns:repeat(2,1fr)}}}}.kpi-card{{background:#fff;border:1px solid var(--br);border-radius:var(--rad);padding:20px 18px 16px;box-shadow:var(--sh);border-top:3px solid var(--bm)}}.kpi-value{{display:block;font-size:26px;font-weight:800;color:var(--bm);line-height:1.1;margin-bottom:5px}}.kpi-label{{display:block;font-size:11.5px;font-weight:700;color:var(--tx);margin-bottom:3px}}.kpi-sub{{display:block;font-size:10.5px;color:var(--tm);opacity:.8}}.footer{{text-align:center;padding:36px 24px;font-size:11px;color:#aaa;border-top:1px solid var(--br);margin-top:40px}}
</style>
</head>
<body>

<div class="cover">
  <p class="cover-meta">Market Analysis Report &nbsp;·&nbsp; Aviation Economics</p>
  <h1>US Airline Flight Routes &amp; Fares<br>Market Analysis (1993-2024)</h1>
  <p class="cover-sub">Structural analysis of pricing dynamics, market concentration, demand patterns, and 30-year fare trends across the US domestic airline market.</p>
  <div class="cover-stats">
    <div class="stat"><span class="stat-value">245k+</span><span class="stat-label">Route-Quarter Observations</span></div>
    <div class="stat"><span class="stat-value">31 yrs</span><span class="stat-label">Time Span</span></div>
    <div class="stat"><span class="stat-value">5</span><span class="stat-label">Business Questions</span></div>
    <div class="stat"><span class="stat-value">Feb 2026</span><span class="stat-label">Zakarias Musa</span></div>
  </div>
</div>

<nav class="nav">
  <a href="#kpi-row">Key Metrics</a>
  <a href="#bq-overview">Overview</a>
  <a href="#section-1">BQ-1 Competition</a>
  <a href="#section-2">BQ-2 Distance</a>
  <a href="#section-3">BQ-3 Demand</a>
  <a href="#section-4">BQ-4 Load Factor</a>
  <a href="#section-5">BQ-5 Trend</a>
  <a href="#exec-summary">Executive Summary</a>
  <a href="#case-study">Case Studies</a>
</nav>

<div class="container">
  <div class="kpi-row" id="kpi-row">
    {''.join(f'''<div class="kpi-card">
      <span class="kpi-value">{v}</span>
      <span class="kpi-label">{l}</span>
      <span class="kpi-sub">{s}</span>
    </div>''' for v,l,s in kpi_cards_data)}
  </div>

  <div class="bq-overview" id="bq-overview">
    <h2>Business Questions</h2>
    <table class="bq-table">
      <thead><tr><th>#</th><th>Business Question</th></tr></thead>
      <tbody>
        <tr><td><span class="bq-pill">BQ-1</span></td><td>Does reduced competition directly translate to higher fares per mile - and by how much?</td></tr>
        <tr><td><span class="bq-pill">BQ-2</span></td><td>Does route distance explain pricing behavior, or do other forces dominate on long-haul?</td></tr>
        <tr><td><span class="bq-pill">BQ-3</span></td><td>Does higher passenger volume discipline fare levels, or do airlines maintain pricing floors?</td></tr>
        <tr><td><span class="bq-pill">BQ-4</span></td><td>Is load factor a meaningful predictor of what passengers pay?</td></tr>
        <tr><td><span class="bq-pill">BQ-5</span></td><td>What does the 30-year fare trend reveal about structural pricing shifts?</td></tr>
      </tbody>
    </table>
  </div>

  {sections_html}

  <div class="exec-summary" id="exec-summary">
    <h2>Executive Summary</h2>
    <p class="exec-sub">Three findings for a strategy or board audience</p>
    {findings_html}
  </div>

  <div class="case-study" id="case-study">
    <div class="cs-header">
      <span class="cs-tag">Applied Analysis</span>
      <h2 class="cs-title">Case Studies &amp; Strategic Recommendations</h2>
      <p class="cs-sub">Three decisions the data makes easier</p>
    </div>

    <div class="cs-grid">

      <div class="cs-card">
        <div class="cs-number">A</div>
        <div class="cs-body">
          <h3 class="cs-card-title">Where Should a Low-Cost Carrier Enter Next?</h3>
          <p class="cs-scenario">A low-cost airline has capital to enter 10 new routes. The question is which ones will generate the fastest return.</p>
          <div class="cs-divider"></div>
          <ul class="cs-list">
            <li>Near-monopoly routes charge <strong>$0.33/mile vs $0.16/mile</strong> on competitive routes &mdash; a 106% structural premium incumbents have held for decades.</li>
            <li>That gap is large enough to enter at <strong>20&ndash;25% below incumbent fares</strong> and still be profitable &mdash; no cost miracle required.</li>
            <li>Sweet spot: dominant share &gt;80%, quarterly volume &gt;150 passengers, no competing airport within 2 hours.</li>
            <li>Budget for a <strong>12&ndash;24 month fare war</strong> from the incumbent before the market stabilises.</li>
          </ul>
          <div class="cs-rec"><span class="cs-rec-label">The call</span>Rank routes by incumbent market share, filter for minimum viable volume, enter at a disciplined discount. The premium is structural &mdash; it will not self-correct without a new entrant.</div>
        </div>
      </div>

      <div class="cs-card">
        <div class="cs-number">B</div>
        <div class="cs-body">
          <h3 class="cs-card-title">Why Is the Pricing Model Underperforming?</h3>
          <p class="cs-scenario">A revenue management team notices their fare prediction model keeps missing. Load factor is one of its main features.</p>
          <div class="cs-divider"></div>
          <ul class="cs-list">
            <li>Load factor correlates at <strong>&minus;0.19 with average fare</strong> &mdash; effectively zero. A 95%-full flight charges the same as a 55%-full one.</li>
            <li>Fares are set <strong>months before departure</strong> via booking curves. By the time load factor is visible, the pricing decision is already locked in.</li>
            <li>Distance (+0.50 correlation) is a legitimate feature and should stay. Load factor should go.</li>
            <li>Replace with: <strong>booking pace</strong>, <strong>competitor capacity changes</strong>, and <strong>route-level market concentration</strong>.</li>
          </ul>
          <div class="cs-rec"><span class="cs-rec-label">The call</span>Drop load factor from pricing models. It belongs in capacity planning &mdash; fleet sizing and frequency decisions &mdash; not fare prediction.</div>
        </div>
      </div>

      <div class="cs-card">
        <div class="cs-number">C</div>
        <div class="cs-body">
          <h3 class="cs-card-title">How Should a Merger Be Evaluated?</h3>
          <p class="cs-scenario">A regulator reviews a proposed merger between two carriers with overlapping domestic routes. Approve, block, or demand divestitures?</p>
          <div class="cs-divider"></div>
          <ul class="cs-list">
            <li>The 2008&ndash;2013 merger wave produced a <strong>+29% fare increase</strong> over 14 years &mdash; the steepest sustained rise in 31 years of data.</li>
            <li>Post-COVID fares are <strong>17% above the pre-COVID peak</strong> despite lower demand &mdash; consolidation’s pricing impact has not reversed.</li>
            <li>The right question is not &ldquo;how many carriers remain nationally&rdquo; but <strong>&ldquo;how many routes shift to near-monopoly?&rdquo;</strong> Each transition means a 14&ndash;106% fare rise on that route.</li>
            <li>Thin corridors (&lt;200 passengers/quarter) are highest risk: once competition leaves, it rarely returns.</li>
          </ul>
          <div class="cs-rec"><span class="cs-rec-label">The call</span>Evaluate at the route level. Require divestitures on any route where post-merger share would exceed 70%, prioritising thin-volume corridors where re-entry is commercially unviable.</div>
        </div>
      </div>

    </div>
  </div>

</div>

<footer class="footer">
  US Airline Flight Routes &amp; Fares 1993-2024 &nbsp;·&nbsp; Zakarias Musa &nbsp;·&nbsp; February 2026
  &nbsp;·&nbsp; Data: US DOT Origin &amp; Destination Survey
</footer>

</body>
</html>"""

out = 'airline_dashboard.html'
with open(out, 'w', encoding='utf-8') as fh:
    fh.write(HTML)

print(f'\nDone.')
print(f'  Dashboard:         {out}  ({len(HTML.encode())//1024} KB)')
print(f'  Individual charts: charts/')
print(f'\nOpen airline_dashboard.html in any browser.')
