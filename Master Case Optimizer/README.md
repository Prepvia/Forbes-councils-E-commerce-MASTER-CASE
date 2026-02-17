# Master Case Optimizer v2.0

Find the best ULINE master case for your product using score-based optimization, pallet utilization, and full cost visibility.

Built for the Forbes Council E-Commerce community. Free, local-first, no account required.

---

## Download & Run in 60 Seconds

1. Open the public repository:  
   `https://github.com/Prepvia/Forbes-councils-E-commerce-MASTER-CASE`
2. Click **Code** > **Download ZIP**
3. Extract the ZIP file
4. Open the `Master Case Optimizer` folder
5. Double-click `START_OPTIMIZER.bat`
6. In your browser, go to `http://localhost:8002`

That is it. No account, no cloud setup, no paid service required.

---

## Current Features

### Optimization modes
- **Unlimited mode**: ranks the best box options regardless of quantity.
- **Limited mode**:
  - **Case Packed**: enforces exact case-packed logic (no empty slots for selected quantity workflows).
  - **Single Units**: supports mixed-box combinations (up to 3 box types) to hit target quantity with better fit/cost.

### 1-100 scoring model
Each recommendation includes normalized scores (1-100):
- **Overall**
- **Pallet efficiency**
- **Volume efficiency**
- **Price efficiency**
- **Ergonomics**

### ULINE catalog (expanded)
- **432 ULINE box configurations total**
  - **224 x 32 ECT lightweight**
  - **208 x 200 lb. test**
- Full pricing tiers per SKU:
  - Qty 25
  - Qty 100
  - Qty 250
  - Qty 500
  - Qty 1,000+
- Direct **ULINE link button** for each recommended SKU.

### Detail panel per selected box
When you click a recommended box, the bottom detail panel shows:
- **Price Tiers** table with savings by quantity
- **Pallet Load visual** (front + top SVG simulation)
- **Pallet Stats**:
  - boxes per layer
  - total layers
  - total boxes
  - stack height on **48 x 40 x 69 in** pallet
  - empty pallet-box weight
  - loaded weight (based on actual product weight input)
- **Ergonomics** view (person-holding-box visual + label)

### Advanced cost options (optional)
- Label cost per box
- Handling cost per box (default $0.25)
- Labor cost (hourly rate + boxes/hour)
- FBA inbound placement strategy:
  - single location
  - 2-3 locations
  - 5+ locations
- FBA fee schedule options (2025 / 2026)

### Compliance and safeguards
- FBA dimensional constraints considered: **36 x 25 x 25 in**
- Pallet height model updated to **69 in**
- Weight input used in optimization and cost logic
- ULINE list pricing disclaimer included (prices are negotiable in real purchasing)

---

## Important Notes
- Loaded pallet weight in the detail panel uses **actual product weight** from user input (not the box's max rating).
- Box shell weight is estimated from surface area and calibrated to realistic corrugated behavior (for example, ~0.80 lb for a 12 x 12 x 12 in 32 ECT box).
- All calculations run locally in your environment.

---

## Quick Start

1. Run the app
   - Windows: `START_OPTIMIZER.bat`
   - Or terminal: `python optimizer_engine.py`

2. Open browser
   - `http://localhost:8002`

3. Enter product data
   - Dimensions (L x W x H in)
   - Weight (lb)
   - Optional units per pack
   - Optional advanced cost settings

4. Click **Find Optimal Box**
   - Review ranked results, score breakdown, and 3D visual
   - Click a SKU to open full bottom detail panel

---

## Tech Stack
- Backend: Python 3.x HTTP server
- Frontend: HTML, CSS, JavaScript
- Visualization: Three.js + custom SVG detail visuals
- Data processing: local only (no external data transmission required for calculations)

---

## Repository
`https://github.com/Prepvia/Forbes-councils-E-commerce-MASTER-CASE`

For a personal narrative and business pitch context, see `FORBES_PITCH.md`.
For vulnerability reporting and security process, see `SECURITY.md`.
