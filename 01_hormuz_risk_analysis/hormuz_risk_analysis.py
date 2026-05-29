# Strait of Hormuz Supply Chain Risk Analyzer
# Author: Sam Asefa
# Data Source: U.S. Energy Information Administration (EIA), Q1 2025
# Description: Models supply chain disruption scenarios for a Strait of Hormuz
# closure and quantifies cost, delay, and risk exposure by importing country.

import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# ── 1. BASELINE TRADE FLOW DATA (EIA Q1 2025) ─────────────────────────────────
data = {
    'country': ['China', 'India', 'South Korea', 'Japan', 'Other Asia', 'Europe', 'United States', 'Other'],
    'flow_mbd': [5.35, 2.96, 2.41, 2.19, 2.80, 1.20, 0.50, 0.69],
    'pct_of_total': [37.7, 14.7, 12.0, 10.9, 13.9, 6.0, 2.5, 2.3],
    'alternative_supply': ['Medium', 'Medium', 'Low', 'Low', 'Low', 'High', 'High', 'Medium']
}

df = pd.DataFrame(data)

# ── 2. DISRUPTION SCENARIOS ───────────────────────────────────────────────────
OIL_PRICE_PER_BARREL = 85

scenarios = {
    'Partial Closure (25%)': 0.25,
    'Full Closure (100%)': 1.00,
    'Cape of Good Hope Reroute': 1.00
}

reroute_days_added = 15
reroute_cost_per_tanker = 2_500_000
tankers_per_day = 15

results = []

for scenario, disruption_pct in scenarios.items():
    for _, row in df.iterrows():
        barrels_lost_per_day = row['flow_mbd'] * 1_000_000 * disruption_pct
        revenue_impact_per_day = barrels_lost_per_day * OIL_PRICE_PER_BARREL

        if scenario == 'Cape of Good Hope Reroute':
            extra_cost = tankers_per_day * reroute_cost_per_tanker
        else:
            extra_cost = 0

        results.append({
            'scenario': scenario,
            'country': row['country'],
            'flow_mbd': row['flow_mbd'],
            'barrels_lost_per_day': round(barrels_lost_per_day),
            'revenue_impact_per_day_usd': round(revenue_impact_per_day),
            'extra_shipping_cost_usd': extra_cost,
            'alternative_supply': row['alternative_supply']
        })

results_df = pd.DataFrame(results)

# ── 3. RISK SCORING ───────────────────────────────────────────────────────────
alternative_supply_score = {'Low': 40, 'Medium': 20, 'High': 5}

df['supply_vulnerability'] = df['alternative_supply'].map(alternative_supply_score)
df['exposure_score'] = df['pct_of_total'] + df['supply_vulnerability']
df['risk_tier'] = pd.cut(
    df['exposure_score'],
    bins=[0, 30, 55, 100],
    labels=['Low Risk', 'Medium Risk', 'High Risk']
)

df_sorted = df.sort_values('exposure_score', ascending=False)

# ── 4. VISUALIZATIONS ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Strait of Hormuz Supply Chain Risk Analysis (EIA Q1 2025)', fontsize=14, fontweight='bold')

axes[0].barh(df_sorted['country'], df_sorted['flow_mbd'], color='steelblue')
axes[0].set_xlabel('Million Barrels Per Day')
axes[0].set_title('Oil Flow by Destination')

colors = ['tomato' if x == 'High Risk' else 'orange' if x == 'Medium Risk' else 'steelblue' for x in df_sorted['risk_tier']]
axes[1].barh(df_sorted['country'], df_sorted['exposure_score'], color=colors)
axes[1].set_xlabel('Risk Exposure Score')
axes[1].set_title('Risk Exposure by Country')

full_closure = results_df[results_df['scenario'] == 'Full Closure (100%)']
axes[2].barh(full_closure['country'], full_closure['revenue_impact_per_day_usd'] / 1_000_000, color='tomato')
axes[2].set_xlabel('USD Million Per Day')
axes[2].set_title('Daily Revenue Impact - Full Closure')

plt.tight_layout()
plt.savefig('hormuz_risk_chart.png')
plt.show()
import numpy as np

# ── HEAT MAP: Normalized Risk Index Model ─────────────────────────────────────
from sklearn.preprocessing import MinMaxScaler

# Define three distinct risk dimensions
heat_data = df_sorted[['country']].copy()

# Dimension 1: Supply Dependence — how much of their oil comes through Hormuz
heat_data['Supply Dependence'] = df_sorted['pct_of_total'].values

# Dimension 2: Reroute Sensitivity — how hard is it to find alternatives
heat_data['Reroute Sensitivity'] = df_sorted['supply_vulnerability'].values

# Dimension 3: Price Exposure — barrels at risk x oil price, normalized by flow
full_closure = results_df[results_df['scenario'] == 'Full Closure (100%)'].copy()
full_closure = full_closure.set_index('country')
heat_data['Price Exposure'] = [
    full_closure.loc[c, 'revenue_impact_per_day_usd'] / 1_000_000 
    if c in full_closure.index else 0 
    for c in df_sorted['country']
]

heat_data = heat_data.set_index('country')

# Normalize all dimensions to 0-1 scale
scaler = MinMaxScaler()
normalized = pd.DataFrame(
    scaler.fit_transform(heat_data),
    columns=heat_data.columns,
    index=heat_data.index
)

fig2, ax = plt.subplots(figsize=(9, 6))
im = ax.imshow(normalized.values, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=1)

ax.set_xticks(range(len(normalized.columns)))
ax.set_xticklabels(normalized.columns, rotation=15)
ax.set_yticks(range(len(normalized.index)))
ax.set_yticklabels(normalized.index)

for i in range(len(normalized.index)):
    for j in range(len(normalized.columns)):
        ax.text(j, i, f'{normalized.values[i, j]:.2f}', 
                ha='center', va='center', color='black', fontsize=9)

plt.colorbar(im, ax=ax, label='Normalized Risk (0 = Low, 1 = High)')
ax.set_title('Hormuz Risk Index Model — Normalized by Dimension (EIA Q1 2025)', fontweight='bold')
plt.tight_layout()
plt.savefig('hormuz_heatmap.png')
plt.show()
# ── 5. RISK ASSESSMENT MEMO ───────────────────────────────────────────────────
memo = """
================================================================================
        SUPPLY CHAIN RISK ASSESSMENT -- STRAIT OF HORMUZ
        Prepared by: Sam Asefa | Data Source: EIA Q1 2025
================================================================================

EXECUTIVE SUMMARY
-----------------
The Strait of Hormuz remains the world's most critical oil transit chokepoint,
carrying 20.1 million barrels per day -- approximately 20% of global petroleum
consumption. Following the Iranian Parliament's June 2025 closure proposal amid
the US-Iran conflict, disruption risk has reached its highest level in decades.

SCENARIO ANALYSIS
-----------------
"""

for scenario in scenarios:
    scenario_data = results_df[results_df['scenario'] == scenario]
    total_barrels = scenario_data['barrels_lost_per_day'].sum()
    total_impact = scenario_data['revenue_impact_per_day_usd'].sum()
    memo += f"  {scenario}\n"
    memo += f"  -> Barrels disrupted per day: {total_barrels:,}\n"
    memo += f"  -> Global revenue impact per day: ${total_impact/1_000_000:,.1f}M USD\n\n"

memo += """
HIGHEST RISK COUNTRIES
----------------------
"""
for _, row in df_sorted[df_sorted['risk_tier'] == 'High Risk'].iterrows():
    memo += f"  {row['country']} -- Risk Score: {row['exposure_score']:.1f} | Alternative Supply: {row['alternative_supply']}\n"

memo += """
KEY FINDINGS
------------
  1. China absorbs 37.7% of Hormuz crude -- a full closure would remove
     5.35M barrels/day from the world's largest oil importer.

  2. Japan and South Korea have virtually no alternative supply routes,
     making them acutely vulnerable to even partial disruptions.

  3. The US and Europe are largely insulated due to domestic production
     and diversified import portfolios.

  4. A Cape of Good Hope reroute adds ~15 days transit time and
     $37.5M/day in additional shipping costs globally.

RECOMMENDATIONS
---------------
  1. Importers with Low alternative supply should accelerate strategic
     petroleum reserve builds and diversify sourcing to West Africa
     and North America.

  2. Energy procurement teams should hedge price exposure via futures
     contracts ahead of any escalation window.

  3. Logistics operators should pre-position rerouting contracts with
     Cape of Good Hope-capable carriers as contingency.
"""

print(memo)

with open('hormuz_risk_assessment.txt', 'w', encoding='utf-8') as f:
    f.write(memo)

print("Risk assessment saved to hormuz_risk_assessment.txt")
