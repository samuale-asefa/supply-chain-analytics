# 01 — Inventory Reorder Point Analysis

## Overview
An automated inventory management tool that reads product data from a CSV, calculates reorder points, flags at-risk products, and emails a purchase order summary when stock levels are critical.

## The Problem It Solves
Stocking out before a replenishment order arrives is one of the most avoidable costs in supply chain operations. This tool automates the monitoring process — flagging products that need restocking and notifying the appropriate team without any manual intervention.

## How It Works
1. Ingests inventory data from a CSV file (editable in Excel or any text editor)
2. Calculates each product's reorder point using the formula:
   > Reorder Point = Daily Demand x Lead Time (days)
3. Flags any SKU that has fallen below its reorder threshold
4. Calculates the exact order quantity needed to return to a safe stock position
5. Loads the dataset into a SQLite database and queries flagged items using SQL
6. Generates a bar chart comparing current stock vs reorder point across all SKUs
7. Automatically dispatches a formatted purchase order to the designated recipient

## Tools Used
Python, pandas, SQLite / SQL, matplotlib, smtplib

## Real World Application
This workflow mirrors what inventory analysts use at companies like Amazon, Walmart, and Home Depot — monitoring thousands of SKUs and triggering replenishment orders automatically when thresholds are crossed.

## What I'd Do With More Data
- Incorporate seasonal demand fluctuations into the reorder calculation
- Add a supplier lead time variability factor for safety stock modeling
- Connect to a live inventory database instead of a static CSV

## Output
![Inventory Chart](inventory_chart.png)