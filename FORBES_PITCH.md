# Master Case Optimizer

A practical tool to remove guesswork from master case selection and reduce hidden logistics costs.

---

## Why This Exists

In many operations, carton selection is based on habit, supplier defaults, or what “looks right.”

The wrong box quietly compounds cost:

- Too large → You pay to ship air, reduce pallet density, and increase freight cost.
- Too small → More cartons, more labels, more labor, more touches.
- Quantities don’t divide cleanly → Leftovers, short shipments, or unplanned waste.

Those small inefficiencies repeat across every shipment.

This tool replaces intuition with measurable tradeoffs.

---

## What It Does

You enter:

- Product dimensions
- Product weight

The optimizer evaluates standard ULINE cartons and scores them based on:

- Pallet utilization
- Box fill rate
- Cost per unit
- Handling efficiency

You receive:

- Ranked carton options
- Cost comparisons
- A 3D packing visualization of how the product fits inside each box

---

## Two Primary Use Cases

### 1️⃣ Ongoing SKU Optimization

If you ship a product regularly, the optimizer:

- Surfaces top-performing carton options
- Compares box price and cost per unit
- Estimates total cost impact

Advanced inputs allow you to include:

- Label cost
- Handling cost per box (e.g. $0.25)
- Labor (hourly rate + boxes per hour)
- FBA inbound placement assumptions

This gives you a closer approximation of true landed operational cost.

---

### 2️⃣ Exact Quantity Planning

If you need to ship a fixed number of units:

- **Case Packed Mode** → One carton type, zero waste, clean division.
- **Mixed Mode** → Combine up to 3 carton sizes to hit your exact unit target with no leftovers.

You see:

- Total spend
- Effective per-unit cost
- Operational tradeoffs before committing

---

## Pricing Assumptions

- Uses ULINE list pricing as a standardized baseline.
- Negotiated rates may vary.
- The goal is consistent comparison logic, not supplier-specific quoting.

---

## Key Principle

The objective is not just cheaper cartons.

The objective is reducing variability and eliminating invisible cost layers in:

- Freight
- Labor
- Pallet density
- Handling complexity

---

## How to Run

1. Download the project folder (`Master Case Optimizer`)
2. Run:

```bash
START_OPTIMIZER.bat
