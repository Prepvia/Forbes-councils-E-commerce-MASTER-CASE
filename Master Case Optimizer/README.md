# Master Case Optimizer v2.0

Find the optimal ULINE Master Case for your product with multi-factor scoring.

## Features

### Two Modes
- **Unlimited Mode**: Find best box regardless of quantity
- **Limited Mode**: Optimize for specific product quantity

### 4 Optimization Factors (1-100 score)
| Factor | Description |
|--------|-------------|
| 📦 **Pallet Efficiency** | How many boxes fit on a 48"×40"×65" pallet |
| 📐 **Volume Efficiency** | Product volume vs box volume (less wasted air) |
| 💰 **Price per Unit** | Cost efficiency per product, not per box |
| 🏋️ **Ergonomics** | Ease of handling (size + weight + shape) |

### Additional Features
- **Top 4 Recommendations** with visual score bars
- **Sort/Filter** by any factor
- **ULINE-only boxes** (40+ standard sizes)
- **Amazon FBA compliant** (36" max side, 25" others, 50 lbs max)

## Constraints
- Max weight: 50 lbs (warning at 45 lbs)
- Max dimensions: 36" × 25" × 25"
- Box weight: 0.6 lbs per sq ft of cardboard

## Usage
1. Run `START_OPTIMIZER.bat`
2. Enter product dimensions and weight
3. Choose mode (Unlimited or Limited)
4. Click "Find Optimal Box"
5. Sort results by your priority factor

## Technical
- Python 3.6+ backend (port 8002)
- Modern HTML5/CSS3/JS frontend
- No external dependencies
