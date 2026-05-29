# Inventory Reorder Point Analysis
# Author: [Your Name]
# Description: Analyzes product inventory levels, calculates reorder points,
# and flags products that need to be restocked using Python, pandas, and SQL.

import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# ── 1. BUILD DATASET ──────────────────────────────────────────────────────────
data = {
    'product': ['Steel Pipes', 'Copper Fittings', 'PVC Valves', 'Brass Connectors', 'Aluminum Flanges'],
    'daily_demand': [20, 35, 15, 50, 10],
    'lead_time_days': [7, 5, 3, 6, 8],
    'current_stock': [200, 100, 60, 400, 50],
    'unit_cost': [45, 22, 8, 15, 60]
}

df = pd.DataFrame(data)

# ── 2. CALCULATE REORDER POINTS ───────────────────────────────────────────────
df['reorder_point'] = df['daily_demand'] * df['lead_time_days']
df['needs_reorder'] = df['current_stock'] < df['reorder_point']
df['units_to_order'] = df.apply(
    lambda row: (row['reorder_point'] - row['current_stock']) if row['needs_reorder'] else 0,
    axis=1
)

# ── 3. VISUALIZE ──────────────────────────────────────────────────────────────
x_pos = range(len(df['product']))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x_pos, df['current_stock'], width, label='Current Stock', color='steelblue')
ax.bar([p + width for p in x_pos], df['reorder_point'], width, label='Reorder Point', color='tomato')
ax.set_xlabel('Product')
ax.set_ylabel('Units')
ax.set_title('Current Stock vs Reorder Point by Product')
ax.set_xticks([p + width/2 for p in x_pos])
ax.set_xticklabels(df['product'], rotation=15)
ax.legend()
plt.tight_layout()
plt.savefig('inventory_chart.png')
plt.show()

# ── 4. STORE AND QUERY WITH SQL ───────────────────────────────────────────────
conn = sqlite3.connect('inventory.db')
df.to_sql('inventory', conn, if_exists='replace', index=False)

query = """
SELECT product, current_stock, reorder_point, units_to_order
FROM inventory
WHERE needs_reorder = 1
ORDER BY units_to_order DESC
"""

result = pd.read_sql(query, conn)
conn.close()

print(result)