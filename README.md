# Inventory Reorder Point Analysis

## What This Does
This tool monitors product inventory levels, identifies reorder triggers, and automatically dispatches a purchase order via email — no manual intervention required. Update the CSV, run the script, and the pipeline handles the rest.

## The Problem It Solves
Stockouts before replenishment orders arrive are one of the most avoidable inefficiencies in supply chain operations. This project automates the demand monitoring and procurement notification process — eliminating the manual effort of tracking stock levels across multiple SKUs.

## How It Works
1. Ingests inventory data from a CSV file (editable in Excel or any text editor)
2. Calculates each product's **reorder point** — the threshold at which a replenishment order must be triggered:
   > Reorder Point = Daily Demand × Lead Time (days)
3. Flags any SKU that has fallen below its reorder threshold
4. Calculates the exact order quantity needed to return to a safe stock position
5. Loads the dataset into a SQLite database and queries flagged items using SQL
6. Generates a bar chart comparing current stock vs reorder point across all SKUs
7. Automatically dispatches a formatted purchase order to the designated recipient when stock is critical

## Tools Used
- Python, pandas, SQLite / SQL, matplotlib, smtplib

## Output
![Inventory Chart](inventory_chart.png)

## Key Features
- **CSV-driven** — swap in any inventory data without touching the codebase
- **SQL querying** — filters and ranks at-risk SKUs by order urgency
- **Automated procurement alerts** — triggers a purchase order the moment a reorder threshold is crossed
- **Scalable** — adaptable to any industry, product type, or order volume