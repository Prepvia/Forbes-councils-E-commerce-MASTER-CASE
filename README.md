# Master Case Optimizer v2.0

Find the optimal ULINE Master Case for your product with multi-factor scoring and full cost estimates.

**Built for the Forbes Council E-Commerce community.** Free, runs locally, no account required.

---

## Features

### Two modes
- **Unlimited mode** — Find the best box regardless of quantity. Get top recommendations with scores, cost per unit, and optional full cost breakdown (labels, handling, labor, FBA inbound).
- **Limited mode** — Optimize for a specific quantity:
  - **Case packed** — One box type only, zero empty slots (perfect for FBA case-packed).
  - **Single units** — Mix up to 3 box types to hit your exact quantity with no leftover.

### Four optimization factors (1–100 score)
| Factor | Description |
|--------|-------------|
| Pallet efficiency | How many boxes fit on a standard 48"×40"×65" pallet |
| Volume efficiency | Product volume vs box volume (less wasted space) |
| Price per unit | Cost efficiency per unit packed |
| Ergonomics | Ease of handling (size, weight, shape) |

### Advanced cost options (optional)
- Label cost per box  
- Handling cost per box (default $0.25)  
- Labor: hourly rate and boxes per hour → cost per box  
- FBA inbound placement: single location / 2–3 locations / 5+ locations  
- FBA fee schedule: until Jan 15, 2026 or from Jan 15, 2026  

Results show a full cost breakdown (boxes, labels, handling, labor, FBA inbound) and total per unit when these options are used.

### Other features
- **38 ULINE standard box SKUs** (6" to 36" range)  
- **3D packing visualization** (Three.js)  
- **Amazon FBA compliant** (36"/25"/25" limits, 50 lbs max)  
- **Weight** used for FBA inbound fee lookup and box weight limits  

---

## Constraints
- Max box weight: 50 lbs (warning at 45 lbs)  
- Max dimensions: 36" × 25" × 25" (FBA)  
- Box prices based on ULINE list pricing (can be negotiated with volume)  

---

## Quick start

1. **Run the app**  
   - Windows: double-click `START_OPTIMIZER.bat`  
   - Or: `python optimizer_engine.py`  

2. **Open in browser**  
   - Go to [http://localhost:8002](http://localhost:8002)  

3. **Enter your product**  
   - Dimensions (L × W × H in inches) and weight (lbs)  
   - For Limited mode, enter total quantity and choose Case Packed or Single Units  

4. **Click “Find Optimal Box”**  
   - Review scores, costs, and 3D view  
   - Use “Advanced cost options” to add labels, handling, labor, and FBA placement for a full cost estimate  

---

## Technical
- **Backend:** Python 3.x (HTTP server on port 8002)  
- **Frontend:** HTML5, CSS3, JavaScript, Three.js  
- **Data:** All processing is local; no data is sent to any server  

---

## Repository
[Forbes-councils-E-commerce-MASTER-CASE](https://github.com/Prepvia/Forbes-councils-E-commerce-MASTER-CASE) — WAZIN / Forbes Council E-Commerce

For a more personal intro and why this tool matters, see [FORBES_PITCH.md](FORBES_PITCH.md).
