# Master Case Optimizer
## Complete Project Documentation

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Input Specifications](#input-specifications)
4. [Output Specifications](#output-specifications)
5. [Algorithm Design](#algorithm-design)
6. [Optimization Criteria](#optimization-criteria)
7. [Constraint System](#constraint-system)
8. [3D Visualization Requirements](#3d-visualization-requirements)
9. [Technical Architecture](#technical-architecture)
10. [Box Pricing System (Future)](#box-pricing-system-future)
11. [Amazon API Integration (Future)](#amazon-api-integration-future)
12. [Implementation Roadmap](#implementation-roadmap)

---

## Project Overview

### Purpose
The **Master Case Optimizer** is a reverse-engineering optimization system that:
- Takes a SINGLE PRODUCT as input (dimensions + weight)
- Recommends the OPTIMAL Master Case size for that product
- Ensures compliance with shipping constraints (36/25/25 rule, 50 lb max)
- Minimizes wasted space and shipping costs
- Provides 3D visualization of the recommended configuration

### Key Difference from Box Stacker
| Box Stacker | Master Case Optimizer |
|-------------|----------------------|
| Given: Master Case dimensions | **Find**: Best Master Case dimensions |
| Given: Multiple products | Given: Single product type |
| Pack products into box | Recommend box for product |

### Use Cases

1. **Single Product Optimization**
   - Client sends one product type
   - System recommends best Master Case size
   - System calculates how many units fit

2. **Pre-Arrival Planning**
   - Know product dimensions before arrival
   - Pre-order optimal boxes
   - Reduce warehouse processing time

3. **Cost Optimization**
   - Calculate cheapest box option
   - Balance between box cost and shipping efficiency

---

## Problem Statement

### The Challenge
Given a product with specific dimensions and weight, find the optimal Master Case that:

1. **Fits the maximum number of units** without exceeding weight limit
2. **Complies with dimensional constraints** (36/25/25 rule)
3. **Minimizes wasted internal space**
4. **Uses standard available box sizes** (when possible)
5. **Keeps total weight under 50 lbs** (warning at 45 lbs)

### Example Scenario
```
Product: Widget X
- Dimensions: 5" × 4" × 3"
- Weight: 0.8 lbs per unit

Question: What is the best Master Case for shipping these widgets?

Possible Answers:
- Option A: 15" × 12" × 9" box = fits 18 units (14.4 lbs)
- Option B: 20" × 16" × 12" box = fits 40 units (32 lbs)
- Option C: 25" × 20" × 15" box = fits 62 units (49.6 lbs) ⚠️ Near limit!

Best Answer: Option C (maximum units while staying under 50 lbs)
```

---

## Input Specifications

### Product Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sku` | String | No | Product SKU/ASIN |
| `name` | String | Yes | Product name |
| `length` | Float | Yes | Product length in inches |
| `width` | Float | Yes | Product width in inches |
| `height` | Float | Yes | Product height in inches |
| `weight` | Float | Yes | Product weight in lbs |
| `fragile` | Boolean | No | If true, may need padding |
| `stackable` | Boolean | No | If false, single layer only |

### Constraints Input (Optional Overrides)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_weight` | Float | 50 | Maximum box weight in lbs |
| `warning_weight` | Float | 45 | Weight warning threshold |
| `max_long_side` | Float | 36 | Maximum for longest dimension |
| `max_other_sides` | Float | 25 | Maximum for other dimensions |
| `box_thickness` | Float | 0.3 | Cardboard thickness in inches |
| `box_weight_per_sqft` | Float | 0.6 | Cardboard weight per sq ft |

### Preferences Input (Optional)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `prefer_standard_sizes` | Boolean | True | Prefer common box sizes |
| `maximize_units` | Boolean | True | Maximize units per box |
| `minimize_boxes` | Boolean | True | Minimize total boxes needed |
| `target_quantity` | Integer | None | Total units to ship |

---

## Output Specifications

### Optimization Result

```json
{
  "product": {
    "name": "Widget X",
    "dimensions": {"length": 5, "width": 4, "height": 3},
    "weight": 0.8
  },
  "recommendations": [
    {
      "rank": 1,
      "master_case": {
        "external_dimensions": {"length": 25, "width": 20, "height": 15},
        "internal_dimensions": {"length": 24.4, "width": 19.4, "height": 14.4},
        "box_weight": 4.58
      },
      "packing": {
        "units_per_box": 62,
        "arrangement": {"along_length": 4, "along_width": 4, "layers": 4},
        "orientation": "Original (5×4×3)",
        "total_product_weight": 49.6,
        "total_weight": 54.18,
        "weight_status": "WARNING"
      },
      "efficiency": {
        "volume_utilization": 0.87,
        "weight_utilization": 0.99
      },
      "warnings": ["Total weight 54.18 lbs exceeds 50 lb limit"]
    },
    {
      "rank": 2,
      "master_case": {
        "external_dimensions": {"length": 20, "width": 16, "height": 12},
        "internal_dimensions": {"length": 19.4, "width": 15.4, "height": 11.4}
      },
      "packing": {
        "units_per_box": 40,
        "arrangement": {"along_length": 4, "along_width": 4, "layers": 2},
        "orientation": "Rotated (5×3×4)",
        "total_product_weight": 32,
        "total_weight": 35.2
      },
      "efficiency": {
        "volume_utilization": 0.71,
        "weight_utilization": 0.70
      },
      "warnings": []
    }
  ],
  "best_recommendation": 2,
  "reasoning": "Recommendation #2 selected: Stays under 50 lb limit while maximizing units"
}
```

### Multi-Box Shipping Plan

When a target quantity is specified:

```json
{
  "target_quantity": 500,
  "shipping_plan": {
    "recommended_box": {
      "dimensions": {"length": 20, "width": 16, "height": 12},
      "units_per_box": 40
    },
    "total_boxes_needed": 13,
    "full_boxes": 12,
    "partial_box_units": 20,
    "total_weight": 457.6,
    "estimated_box_cost": null
  }
}
```

---

## Algorithm Design

### Phase 1: Calculate Maximum Units Per Orientation

For each of the 6 product orientations, calculate maximum units:

```python
def calculate_max_units(product, box_internal):
    """Calculate maximum units that fit in a box"""
    max_units = 0
    best_arrangement = None
    
    for orientation in get_orientations(product):
        pL, pW, pH = orientation  # Product dimensions in this orientation
        
        # Calculate how many fit along each axis
        along_length = floor(box_internal.length / pL)
        along_width = floor(box_internal.width / pW)
        along_height = floor(box_internal.height / pH)
        
        units = along_length * along_width * along_height
        
        if units > max_units:
            max_units = units
            best_arrangement = {
                'orientation': orientation,
                'along_length': along_length,
                'along_width': along_width,
                'layers': along_height
            }
    
    return max_units, best_arrangement
```

### Phase 2: Weight-Constrained Optimization

```python
def optimize_for_weight(product, box, max_weight=50):
    """Find maximum units that fit within weight limit"""
    max_units, arrangement = calculate_max_units(product, box.internal)
    
    # Calculate total weight with all units
    box_weight = calculate_box_weight(box)
    total_product_weight = max_units * product.weight
    total_weight = box_weight + total_product_weight
    
    # If over weight limit, reduce units
    if total_weight > max_weight:
        available_product_weight = max_weight - box_weight
        max_units = floor(available_product_weight / product.weight)
        
        # Recalculate arrangement with fewer units
        arrangement = recalculate_arrangement(max_units, product, box)
    
    return max_units, arrangement, total_weight
```

### Phase 3: Box Size Search

#### Strategy 1: Standard Box Sizes
Test common box sizes and find best fit:

```python
STANDARD_BOXES = [
    (12, 9, 6),
    (14, 10, 8),
    (16, 12, 10),
    (18, 14, 12),
    (20, 16, 12),
    (22, 18, 14),
    (24, 18, 16),
    (24, 20, 18),
    (25, 20, 15),
    (30, 20, 15),
    (36, 24, 18),
    (36, 25, 25),  # Maximum allowed
]

def find_best_standard_box(product, max_weight=50):
    """Find best standard box for product"""
    results = []
    
    for box_dims in STANDARD_BOXES:
        if not validate_dimensions(box_dims):
            continue
            
        box = MasterCase(*box_dims)
        units, arrangement, weight = optimize_for_weight(product, box, max_weight)
        
        if units > 0 and weight <= max_weight:
            efficiency = calculate_efficiency(product, box, units)
            results.append({
                'box': box,
                'units': units,
                'weight': weight,
                'efficiency': efficiency
            })
    
    # Sort by units (descending), then by efficiency
    results.sort(key=lambda r: (-r['units'], -r['efficiency']))
    return results
```

#### Strategy 2: Custom Box Calculation
Calculate optimal custom dimensions:

```python
def calculate_optimal_custom_box(product, target_units=None, max_weight=50):
    """Calculate optimal custom box dimensions"""
    pL, pW, pH = sorted([product.length, product.width, product.height], reverse=True)
    
    # Calculate weight-limited units
    max_product_weight = max_weight - estimated_min_box_weight(product)
    weight_limited_units = floor(max_product_weight / product.weight)
    
    if target_units:
        target_units = min(target_units, weight_limited_units)
    else:
        target_units = weight_limited_units
    
    # Find best arrangement for target units
    best_box = None
    best_efficiency = 0
    
    for n_layers in range(1, 10):
        units_per_layer = ceil(target_units / n_layers)
        
        for n_length in range(1, 20):
            n_width = ceil(units_per_layer / n_length)
            
            # Calculate box dimensions
            box_length = pL * n_length + 0.6  # Add thickness
            box_width = pW * n_width + 0.6
            box_height = pH * n_layers + 0.6
            
            # Validate dimensions (36/25/25 rule)
            dims = sorted([box_length, box_width, box_height], reverse=True)
            if dims[0] > 36 or dims[1] > 25 or dims[2] > 25:
                continue
            
            # Calculate efficiency
            actual_units = n_length * n_width * n_layers
            box = MasterCase(box_length, box_width, box_height)
            total_weight = box.weight + (actual_units * product.weight)
            
            if total_weight <= max_weight:
                efficiency = calculate_efficiency(product, box, actual_units)
                if efficiency > best_efficiency:
                    best_efficiency = efficiency
                    best_box = {
                        'dimensions': (box_length, box_width, box_height),
                        'units': actual_units,
                        'arrangement': (n_length, n_width, n_layers),
                        'weight': total_weight,
                        'efficiency': efficiency
                    }
    
    return best_box
```

---

## Optimization Criteria

### Primary Criteria (In Order of Priority)

1. **Weight Compliance**: Total weight ≤ 50 lbs (HARD LIMIT)
2. **Dimensional Compliance**: 36/25/25 rule (HARD LIMIT)
3. **Maximize Units**: Pack as many units as possible
4. **Volume Efficiency**: Minimize wasted space

### Secondary Criteria

5. **Standard Size Preference**: Use common box sizes when possible
6. **Cost Optimization**: Consider box pricing (future feature)
7. **Shipping Efficiency**: Consider dimensional weight pricing

### Scoring Formula

```python
def calculate_score(result, preferences):
    score = 0
    
    # Units score (40% weight)
    score += (result.units / max_possible_units) * 40
    
    # Volume efficiency score (30% weight)
    score += result.volume_efficiency * 30
    
    # Weight efficiency score (20% weight)
    score += result.weight_efficiency * 20
    
    # Standard size bonus (10% weight)
    if result.is_standard_size:
        score += 10
    
    # Penalties
    if result.total_weight > 45:
        score -= 5  # Warning zone penalty
    
    return score
```

---

## Constraint System

### Dimensional Constraints

```python
def validate_box_dimensions(length, width, height):
    """Validate Master Case dimensions against Amazon rules"""
    dims = sorted([length, width, height], reverse=True)
    
    errors = []
    warnings = []
    
    # Check largest dimension
    if dims[0] > 36:
        errors.append(f"Longest side {dims[0]}\" exceeds 36\" maximum")
    elif dims[0] >= 34:
        warnings.append(f"Longest side {dims[0]}\" is close to 36\" limit")
    
    # Check other dimensions
    if dims[1] > 25:
        errors.append(f"Second dimension {dims[1]}\" exceeds 25\" maximum")
    elif dims[1] >= 23:
        warnings.append(f"Second dimension {dims[1]}\" is close to 25\" limit")
    
    if dims[2] > 25:
        errors.append(f"Third dimension {dims[2]}\" exceeds 25\" maximum")
    elif dims[2] >= 23:
        warnings.append(f"Third dimension {dims[2]}\" is close to 25\" limit")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }
```

### Weight Constraints

```python
def validate_weight(total_weight, max_weight=50, warning_threshold=45):
    """Validate total box weight"""
    if total_weight > max_weight:
        return {
            'valid': False,
            'status': 'EXCEEDED',
            'message': f"Weight {total_weight:.1f} lbs exceeds {max_weight} lb limit"
        }
    elif total_weight > warning_threshold:
        return {
            'valid': True,
            'status': 'WARNING',
            'message': f"Weight {total_weight:.1f} lbs approaching {max_weight} lb limit"
        }
    else:
        return {
            'valid': True,
            'status': 'OK',
            'message': f"Weight {total_weight:.1f} lbs is within limits"
        }
```

---

## 3D Visualization Requirements

### Visualization Elements

1. **Master Case (Transparent)**
   - Wireframe or semi-transparent box
   - Shows internal dimensions
   - Color: Light blue with visible edges

2. **Products Inside**
   - Solid colored cubes/boxes
   - Different opacity per layer
   - Grid arrangement visible

3. **Annotations**
   - Dimension labels
   - Unit count per layer
   - Total units display

### Interactive Features

| Feature | Description |
|---------|-------------|
| **Rotate** | Mouse drag to rotate view |
| **Zoom** | Scroll wheel zoom |
| **Explode** | Separate layers for clarity |
| **Compare** | Side-by-side comparison of options |
| **Animate** | Show packing sequence |

### Comparison View
Display multiple box options side by side:

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Option 1   │  │  Option 2   │  │  Option 3   │
│             │  │             │  │             │
│  40 units   │  │  62 units   │  │  24 units   │
│  35.2 lbs   │  │  49.6 lbs   │  │  22.8 lbs   │
│  71% eff    │  │  87% eff    │  │  65% eff    │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (HTML/JS)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Product    │  │  3D Compare │  │  Recommendations    │  │
│  │  Input Form │  │  View       │  │  Panel              │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Python)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  API Server │  │ Optimization│  │  Box Database       │  │
│  │  (HTTP)     │  │  Engine     │  │  (Standard Sizes)   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
Master Case Optimizer/
├── master_case_optimizer.html    # Main UI (3D visualization)
├── optimizer_engine.py           # Backend server & algorithm
├── START_OPTIMIZER.bat           # Windows launcher
├── README.md                     # Quick start guide
├── PROJECT_DOCUMENTATION.md      # This file
├── box_database.json             # Standard box sizes
└── pricing/                      # Future: Box pricing data
    └── supplier_prices.json
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/optimize` | POST | Calculate optimal box recommendations |
| `/api/boxes` | GET | Get list of standard box sizes |
| `/api/validate` | POST | Validate product dimensions |
| `/api/compare` | POST | Compare multiple box options |

---

## Box Pricing System (Future)

### Pricing Data Structure

```json
{
  "suppliers": [
    {
      "name": "ULINE",
      "boxes": [
        {
          "sku": "S-4321",
          "dimensions": [12, 9, 6],
          "price_per_unit": 0.85,
          "price_per_bundle": 18.50,
          "bundle_quantity": 25,
          "lead_time_days": 3
        }
      ]
    }
  ]
}
```

### Cost Optimization

```python
def optimize_with_cost(product, target_quantity, pricing_data):
    """Find most cost-effective shipping configuration"""
    options = []
    
    for supplier in pricing_data['suppliers']:
        for box in supplier['boxes']:
            units_per_box = calculate_units(product, box)
            boxes_needed = ceil(target_quantity / units_per_box)
            
            box_cost = boxes_needed * box['price_per_unit']
            # Add estimated shipping cost based on dimensional weight
            shipping_cost = estimate_shipping(box, boxes_needed)
            
            total_cost = box_cost + shipping_cost
            
            options.append({
                'supplier': supplier['name'],
                'box': box,
                'boxes_needed': boxes_needed,
                'box_cost': box_cost,
                'shipping_cost': shipping_cost,
                'total_cost': total_cost
            })
    
    return sorted(options, key=lambda x: x['total_cost'])
```

---

## Amazon API Integration (Future)

### Purpose
Fetch product dimensions directly from Amazon to enable pre-arrival planning.

### Data Flow

```
1. User enters ASIN/SKU
2. System queries Amazon Product Advertising API
3. Retrieve: dimensions, weight, title, image
4. Auto-populate optimization form
5. Calculate optimal Master Case
6. Pre-order boxes before products arrive
```

### Amazon API Response (Expected)

```json
{
  "asin": "B00EXAMPLE",
  "title": "Widget X Premium Edition",
  "dimensions": {
    "length": {"value": 5.0, "unit": "inches"},
    "width": {"value": 4.0, "unit": "inches"},
    "height": {"value": 3.0, "unit": "inches"}
  },
  "weight": {"value": 0.8, "unit": "pounds"},
  "image_url": "https://..."
}
```

### Pre-Arrival Workflow

```
1. Receive shipment notification with ASINs
2. Batch query Amazon for all product dimensions
3. Calculate optimal boxes for each product
4. Generate box order list
5. Order boxes from supplier
6. Boxes arrive before products
7. Products arrive → immediate packing
```

---

## Implementation Roadmap

### Step 1: Core Algorithm
- [ ] Implement product orientation testing
- [ ] Implement unit counting algorithm
- [ ] Implement weight-constrained optimization
- [ ] Create standard box database
- [ ] Implement box search algorithm

### Step 2: API Server
- [ ] Create HTTP server
- [ ] Implement `/api/optimize` endpoint
- [ ] Implement `/api/boxes` endpoint
- [ ] Add input validation
- [ ] Add error handling

### Step 3: Frontend - Input
- [ ] Create product input form
- [ ] Add dimension validation (real-time)
- [ ] Add weight calculation display
- [ ] Create preferences panel

### Step 4: Frontend - Results
- [ ] Create recommendations list
- [ ] Show comparison table
- [ ] Add detail expansion
- [ ] Create export function

### Step 5: Frontend - 3D Visualization
- [ ] Set up Three.js scene
- [ ] Create transparent box visualization
- [ ] Create product grid visualization
- [ ] Implement comparison view
- [ ] Add animation support

### Step 6: Testing & Optimization
- [ ] Test with various product sizes
- [ ] Benchmark algorithm performance
- [ ] Optimize for edge cases
- [ ] Polish UI/UX

### Future Steps
- [ ] Add box pricing database
- [ ] Implement cost optimization
- [ ] Add Amazon API integration
- [ ] Create batch processing
- [ ] Add ML-based recommendations

---

## Appendix: Standard Box Sizes Reference

### Common Amazon-Compliant Sizes

| Size Code | External (L×W×H) | Internal (L×W×H) | Est. Weight |
|-----------|------------------|------------------|-------------|
| XS-1 | 10" × 8" × 6" | 9.4" × 7.4" × 5.4" | 1.2 lbs |
| S-1 | 12" × 9" × 6" | 11.4" × 8.4" × 5.4" | 1.5 lbs |
| S-2 | 14" × 10" × 8" | 13.4" × 9.4" × 7.4" | 1.9 lbs |
| M-1 | 16" × 12" × 10" | 15.4" × 11.4" × 9.4" | 2.5 lbs |
| M-2 | 18" × 14" × 12" | 17.4" × 13.4" × 11.4" | 3.2 lbs |
| L-1 | 20" × 16" × 12" | 19.4" × 15.4" × 11.4" | 3.6 lbs |
| L-2 | 22" × 18" × 14" | 21.4" × 17.4" × 13.4" | 4.3 lbs |
| XL-1 | 24" × 20" × 16" | 23.4" × 19.4" × 15.4" | 5.0 lbs |
| XL-2 | 24" × 24" × 18" | 23.4" × 23.4" × 17.4" | 5.8 lbs |
| MAX | 36" × 25" × 25" | 35.4" × 24.4" × 24.4" | 8.2 lbs |

---

## Conclusion

The **Master Case Optimizer** provides the inverse functionality of the Box Stacker:
- **Box Stacker**: Given a box, pack products inside
- **Master Case Optimizer**: Given a product, find the best box

This tool is essential for:
1. Reducing shipping costs
2. Pre-planning box orders
3. Optimizing warehouse operations
4. Ensuring compliance with shipping rules

Combined with future Amazon API integration and box pricing data, this system will enable fully automated shipping preparation planning.

---

*Document Version: 1.0*
*Last Updated: February 2026*
*Related Projects: Pallet Stacker 1.0, Box Stacker*
