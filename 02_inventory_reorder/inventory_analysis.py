# Inventory Reorder Point Analysis
# Author: Sam Asefa
# Description: Reads inventory data from a CSV, calculates reorder points,
# flags products that need restocking, and generates a purchase order summary.

import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# ── 1. LOAD DATA FROM CSV ─────────────────────────────────────────────────────
df = pd.read_csv('inventory.csv')

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

# ── 5. PURCHASE ORDER SUMMARY ─────────────────────────────────────────────────
print("=" * 50)
print("       AUTOMATED PURCHASE ORDER SUMMARY")
print("=" * 50)

if result.empty:
    print("All products are sufficiently stocked.")
else:
    for _, row in result.iterrows():
        print(f"\nProduct:        {row['product']}")
        print(f"Current Stock:  {int(row['current_stock'])} units")
        print(f"Reorder Point:  {int(row['reorder_point'])} units")
        print(f"Units to Order: {int(row['units_to_order'])} units")
        print("-" * 50)

print("\nPurchase order generated. Ready to send.")
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── 6. EMAIL PURCHASE ORDER ───────────────────────────────────────────────────
SENDER = "towsonuniversity8@gmail.com"
RECEIVER = "towsonuniversity8@gmail.com"
APP_PASSWORD = "zxbo ekps uudw zjpr"

if not result.empty:
    body = "AUTOMATED PURCHASE ORDER\n\n"
    for _, row in result.iterrows():
        body += f"Product: {row['product']}\n"
        body += f"Current Stock: {int(row['current_stock'])} units\n"
        body += f"Reorder Point: {int(row['reorder_point'])} units\n"
        body += f"Units to Order: {int(row['units_to_order'])} units\n"
        body += "-" * 40 + "\n\n"

    msg = MIMEMultipart()
    msg['From'] = SENDER
    msg['To'] = RECEIVER
    msg['Subject'] = "⚠️ Inventory Alert: Reorder Required"
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER, APP_PASSWORD)
        server.sendmail(SENDER, RECEIVER, msg.as_string())

    print("Email alert sent successfully.")