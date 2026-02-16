"""
Master Case Optimizer v2.0
==========================
Find the optimal Master Case size for a given product.

OPTIMIZATION FACTORS (scored 1-100):
1. Pallet Efficiency - How well boxes fit on 48x40x65" pallet
2. Volume Efficiency - Product volume vs box internal volume
3. Price per Product - Cost efficiency per unit
4. Ergonomics - Ease of handling (size + weight)

TWO MODES:
1. Unlimited - Infinite products, find best box
2. Limited - Specific quantity, optimize for that amount
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any, Set
import json
import math
import os
import sys

sys.stdout.reconfigure(line_buffering=True)

# =============================================================================
# PALLET SPECIFICATIONS
# =============================================================================

PALLET_LENGTH = 48  # inches
PALLET_WIDTH = 40   # inches
PALLET_HEIGHT = 65  # inches (max stack height)

# =============================================================================
# ULINE BOX DATABASE (ONLY STANDARD SIZES)
# =============================================================================

ULINE_BOXES = [
    # (Length, Width, Height, Price, SKU)
    # Small boxes
    (6, 6, 6, 0.42, "S-4511"),
    (6, 6, 4, 0.35, "S-4512"),
    (8, 6, 4, 0.38, "S-4856"),
    (8, 8, 8, 0.65, "S-4515"),
    (10, 8, 6, 0.52, "S-4080"),
    (10, 10, 6, 0.72, "S-4516"),
    (10, 10, 10, 0.95, "S-4519"),
    # Medium boxes
    (12, 9, 6, 0.58, "S-19865"),
    (12, 10, 8, 0.72, "S-4082"),
    (12, 12, 8, 0.85, "S-4329"),
    (12, 12, 12, 1.15, "S-4523"),
    (14, 10, 8, 0.78, "S-11362"),
    (14, 12, 10, 0.95, "S-4331"),
    (14, 14, 14, 1.65, "S-4527"),
    # Large boxes
    (16, 12, 8, 0.88, "S-4333"),
    (16, 12, 10, 0.98, "S-4334"),
    (16, 12, 12, 1.12, "S-4335"),
    (16, 16, 16, 2.15, "S-4531"),
    (18, 12, 10, 1.05, "S-4337"),
    (18, 14, 12, 1.28, "S-4338"),
    (18, 16, 14, 1.55, "S-22188"),
    (18, 18, 18, 2.65, "S-4535"),
    # XL boxes
    (20, 14, 10, 1.18, "S-16748"),
    (20, 16, 12, 1.42, "S-4341"),
    (20, 18, 14, 1.72, "S-22191"),
    (20, 20, 12, 1.85, "S-4463"),
    (20, 20, 20, 3.25, "S-4539"),
    (22, 16, 14, 1.68, "S-22194"),
    (22, 18, 16, 2.05, "S-22197"),
    (22, 22, 22, 3.95, "S-4543"),
    # XXL boxes
    (24, 16, 12, 1.52, "S-4346"),
    (24, 18, 14, 1.88, "S-22200"),
    (24, 18, 18, 2.25, "S-4348"),
    (24, 20, 16, 2.35, "S-22203"),
    (24, 24, 18, 3.15, "S-4470"),
    (24, 24, 24, 4.25, "S-4547"),
    # Jumbo boxes
    (30, 20, 15, 2.35, "S-22206"),
    (30, 24, 18, 3.25, "S-22209"),
    (32, 18, 12, 2.15, "S-22212"),
    # FBA Max boxes
    (36, 24, 18, 3.85, "S-22215"),
    (36, 24, 24, 4.45, "S-22218"),
]

# =============================================================================
# FBA INBOUND PLACEMENT FEES (per unit)
# Placement: single = 1 location, 2-3 = partial, 5+ = optimized
# Fee as (min, max) USD; we use midpoint. Weight in lbs.
# =============================================================================

FBA_STANDARD_2025 = {
    'small_standard': {
        'weight_tiers': [(0, 1.0)],
        'single': (0.16, 0.30),
        'optimized': (0, 0),
    },
    'large_standard': {
        'weight_tiers': [(0, 0.75), (0.75, 1.5), (1.5, 3), (3, 20)],
        'single': [(0.18, 0.34), (0.22, 0.41), (0.27, 0.49), (0.37, 0.68)],
        'optimized': (0, 0),
    },
}

FBA_STANDARD_2026 = {
    'small_standard': {
        'weight_tiers': [(0, 0.5), (0.5, 1.0)],
        'single': [(0.14, 0.32), (0.16, 0.32)],
        'optimized': (0, 0),
    },
    'large_standard': {
        'weight_tiers': [(0, 0.75), (0.75, 1.5), (1.5, 3), (3, 5), (5, 7), (7, 10), (10, 15), (15, 20)],
        'single': [(0.20, 0.40), (0.24, 0.50), (0.34, 0.60), (0.38, 0.76), (0.40, 0.98), (0.42, 1.20), (0.44, 1.50), (0.55, 1.90)],
        'optimized': (0, 0),
    },
}

FBA_BULKY_2025 = {
    'large_bulky': {
        'weight_tiers': [(0, 5), (5, 12), (12, 28), (28, 42), (42, 50)],
        'single': [(1.10, 1.60), (1.75, 2.40), (2.74, 3.50), (3.95, 4.95), (4.80, 5.95)],
        'partial': [(0.55, 1.10), (0.65, 1.75), (0.81, 2.19), (1.05, 2.83), (1.23, 3.32)],
        'optimized': (0, 0),
    },
}

FBA_BULKY_2026 = {
    'small_bulky': {
        'weight_tiers': [(0, 5), (5, 12), (12, 28), (28, 42), (42, 50)],
        'single': [(1.10, 1.60), (1.75, 2.40), (2.74, 3.50), (3.95, 4.95), (4.80, 5.95)],
        'partial': [(0.55, 1.10), (0.65, 1.75), (0.81, 2.19), (1.05, 2.83), (1.23, 3.32)],
        'optimized': (0, 0),
    },
    'large_bulky': {
        'weight_tiers': [(0, 5), (5, 12), (12, 28), (28, 42), (42, 50)],
        'single': [(1.30, 1.80), (2.10, 2.90), (3.40, 4.10), (4.70, 5.60), (5.50, 6.50)],
        'partial': [(0.55, 1.25), (0.65, 1.80), (0.81, 2.30), (1.05, 2.95), (1.23, 3.50)],
        'optimized': (0, 0),
    },
}


def _product_size_tier(length_in: float, width_in: float, height_in: float, schedule_2026: bool) -> Optional[str]:
    dims = sorted([length_in, width_in, height_in], reverse=True)
    g, m, s = dims[0], dims[1], dims[2]
    if g <= 15 and m <= 12 and s <= 0.75:
        return 'small_standard'
    if g <= 18 and m <= 14 and s <= 8:
        return 'large_standard'
    if schedule_2026:
        if g <= 37 and m <= 28 and s <= 20:
            return 'small_bulky'
        if g <= 59 and m <= 33 and s <= 33:
            return 'large_bulky'
    else:
        if g <= 59 and m <= 33 and s <= 33:
            return 'large_bulky'
    return None


def get_fba_inbound_fee_per_unit(
    length_in: float, width_in: float, height_in: float, weight_lb: float,
    placement: str, schedule_2026: bool
) -> Tuple[Optional[float], Optional[str]]:
    """Returns (fee_per_unit_usd, size_tier_label) or (None, None). placement: 'single'|'2-3'|'5+'"""
    tier = _product_size_tier(length_in, width_in, height_in, schedule_2026)
    if not tier:
        return None, None
    std = FBA_STANDARD_2026 if schedule_2026 else FBA_STANDARD_2025
    bulky = FBA_BULKY_2026 if schedule_2026 else FBA_BULKY_2025
    if tier in std:
        table = std[tier]
    elif tier in bulky:
        table = bulky[tier]
    else:
        return None, None
    weight_tiers = table['weight_tiers']
    col = 'optimized' if placement == '5+' else ('partial' if placement == '2-3' else 'single')
    if col == 'optimized' and tier in ('small_standard', 'large_standard'):
        return 0.0, tier
    fees = table.get(col)
    if fees is None:
        fees = table.get('single')
    if isinstance(fees, list):
        for i, (lo, hi) in enumerate(weight_tiers):
            if lo < weight_lb <= hi:
                fee_range = fees[i]
                mid = (fee_range[0] + fee_range[1]) / 2
                return round(mid, 2), tier
        return None, tier
    if isinstance(fees, tuple):
        if weight_tiers and len(weight_tiers) == 1:
            lo, hi = weight_tiers[0]
            if lo < weight_lb <= hi:
                mid = (fees[0] + fees[1]) / 2
                return round(mid, 2), tier
        return None, tier
    return None, tier


def compute_cost_breakdown(
    product: 'Product',
    total_boxes: int,
    total_units: int,
    box_cost_total: float,
    label_per_box: float = 0,
    handling_per_box: float = 0,
    labor_hourly: Optional[float] = None,
    boxes_per_hour: Optional[float] = None,
    fba_placement: str = '5+',
    fba_schedule_2026: bool = False,
) -> Dict[str, Any]:
    """
    Returns a cost breakdown dict: boxes, labels, handling, labor, fba_inbound, total, total_per_unit.
    All monetary values in USD. Optional fields omitted when not provided.
    """
    out = {
        'boxes': round(box_cost_total, 2),
        'labels': round(label_per_box * total_boxes, 2),
        'handling': round(handling_per_box * total_boxes, 2),
        'labor': 0.0,
        'fba_inbound': 0.0,
        'fba_tier': None,
    }
    if labor_hourly is not None and boxes_per_hour is not None and boxes_per_hour > 0:
        out['labor'] = round((labor_hourly / boxes_per_hour) * total_boxes, 2)
    fee_per_unit, fba_tier = get_fba_inbound_fee_per_unit(
        product.length, product.width, product.height, product.weight,
        fba_placement, fba_schedule_2026
    )
    if fee_per_unit is not None and total_units > 0:
        out['fba_inbound'] = round(fee_per_unit * total_units, 2)
        out['fba_tier'] = fba_tier
        out['fba_per_unit'] = round(fee_per_unit, 2)
    out['total'] = round(out['boxes'] + out['labels'] + out['handling'] + out['labor'] + out['fba_inbound'], 2)
    out['total_per_unit'] = round(out['total'] / total_units, 4) if total_units > 0 else 0
    return out


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Product:
    """Product to optimize Master Case for"""
    name: str
    length: float
    width: float
    height: float
    weight: float
    quantity: int = -1  # -1 = unlimited
    
    @property
    def volume(self):
        return self.length * self.width * self.height


@dataclass
class BoxConfig:
    """A box configuration with all metrics"""
    sku: str
    length: float
    width: float
    height: float
    price: float
    
    # Packing info
    units_per_box: int
    arrangement: Tuple[int, int, int]  # (along_L, along_W, layers)
    orientation: str
    
    # For limited mode
    boxes_needed: int = 0
    total_units: int = 0
    leftover: int = 0
    
    # Scores (1-100)
    pallet_score: float = 0
    volume_score: float = 0
    price_score: float = 0
    ergonomic_score: float = 0
    overall_score: float = 0
    
    # Metrics
    price_per_unit: float = 0
    volume_utilization: float = 0
    boxes_per_pallet: int = 0
    total_weight: float = 0
    
    # Warnings
    warnings: List[str] = None


# =============================================================================
# OPTIMIZER
# =============================================================================

class MasterCaseOptimizer:
    MAX_WEIGHT = 50.0
    WARNING_WEIGHT = 45.0
    
    def __init__(self, product: Product, limited_mode: str = 'case_packed'):
        self.product = product
        self.is_limited = product.quantity > 0
        self.limited_mode = limited_mode  # 'case_packed' or 'single_units'
    
    def optimize(self) -> List[BoxConfig]:
        """Find optimal box configurations"""
        results = []
        
        for length, width, height, price, sku in ULINE_BOXES:
            config = self._evaluate_box(length, width, height, price, sku)
            if config and config.units_per_box > 0:
                results.append(config)
        
        if not results:
            return []
        
        # Calculate normalized scores
        self._normalize_scores(results)
        
        # Sort by overall score (highest first)
        results.sort(key=lambda c: -c.overall_score)
        
        return results[:10]  # Top 10
    
    def optimize_case_packed(self) -> Dict:
        """
        Case Packed Mode: ONE box type only (all identical boxes).
        RULE: Zero empty slots. Every unit must fit with no waste.
        If no perfect fit exists, return quantity suggestions.
        """
        all_boxes = []
        
        for length, width, height, price, sku in ULINE_BOXES:
            config = self._evaluate_box(length, width, height, price, sku)
            if config and config.units_per_box > 0:
                all_boxes.append(config)
        
        if not all_boxes:
            return {'combinations': [], 'suggested_quantities': []}
        
        self._normalize_scores(all_boxes)
        all_boxes.sort(key=lambda c: -c.overall_score)
        
        qty = self.product.quantity
        perfect_fits = []
        suggested_quantities = set()
        
        for box in all_boxes:
            n = box.units_per_box
            
            if qty % n == 0:
                boxes_needed = qty // n
                perfect_fits.append({
                    'type': 'case_packed',
                    'primary': self._box_to_dict(box, boxes_needed, qty),
                    'secondary': None,
                    'total_boxes': boxes_needed,
                    'total_cost': round(boxes_needed * box.price, 2),
                    'cost_per_unit': round(box.price / n, 4),
                    'total_units': qty,
                    'total_capacity': qty,
                    'empty_slots': 0,
                    'fill_efficiency': 100.0,
                    'combined_score': box.overall_score
                })
            else:
                lower = (qty // n) * n
                upper = lower + n
                if lower > 0:
                    suggested_quantities.add(lower)
                suggested_quantities.add(upper)
        
        # Sort by score, then cost
        perfect_fits.sort(key=lambda c: (-c['combined_score'], c['total_cost']))
        
        # Deduplicate by SKU
        seen = set()
        unique = []
        for c in perfect_fits:
            key = c['primary']['sku']
            if key not in seen:
                seen.add(key)
                unique.append(c)
        
        # Build quantity suggestions sorted by proximity to requested qty
        nearby = sorted(suggested_quantities, key=lambda x: (abs(x - qty), x))
        nearby = [q for q in nearby if q > 0][:8]
        
        return {
            'combinations': unique[:6],
            'suggested_quantities': nearby if not unique else []
        }
    
    def optimize_single_units(self) -> List[Dict]:
        """
        Single Units Mode: Use up to 3 different box types for EXACT quantity.
        No leftover allowed - every unit accounted for.
        """
        all_boxes = []
        
        for length, width, height, price, sku in ULINE_BOXES:
            config = self._evaluate_box(length, width, height, price, sku)
            if config and config.units_per_box > 0:
                all_boxes.append(config)
        
        if not all_boxes:
            return []
        
        self._normalize_scores(all_boxes)
        all_boxes.sort(key=lambda c: -c.overall_score)
        
        qty = self.product.quantity
        combinations = []
        
        top_boxes = all_boxes[:20]
        
        # 1-box solutions (perfect divisor)
        for b1 in top_boxes:
            if qty % b1.units_per_box == 0:
                count = qty // b1.units_per_box
                cost = round(count * b1.price, 2)
                combinations.append({
                    'type': '1-box',
                    'boxes': [self._box_to_dict(b1, count, count * b1.units_per_box)],
                    'total_boxes': count,
                    'total_cost': cost,
                    'cost_per_unit': round(cost / qty, 4),
                    'total_units': qty,
                    'leftover': 0,
                    'combined_score': b1.overall_score
                })
        
        # 2-box combinations (different SKUs only)
        for i, b1 in enumerate(top_boxes[:15]):
            for b2 in top_boxes[i+1:15]:
                if b1.sku == b2.sku:
                    continue
                max_n1 = qty // b1.units_per_box
                for n1 in range(1, max_n1 + 1):
                    remaining = qty - n1 * b1.units_per_box
                    if remaining <= 0:
                        continue
                    if remaining % b2.units_per_box == 0:
                        n2 = remaining // b2.units_per_box
                        if n2 > 0:
                            total = n1 + n2
                            score = (b1.overall_score * n1 + b2.overall_score * n2) / total
                            cost = round(n1 * b1.price + n2 * b2.price, 2)
                            
                            boxes_list = [
                                self._box_to_dict(b1, n1, n1 * b1.units_per_box),
                                self._box_to_dict(b2, n2, n2 * b2.units_per_box)
                            ]
                            
                            combinations.append({
                                'type': '2-box mix',
                                'boxes': boxes_list,
                                'total_boxes': total,
                                'total_cost': cost,
                                'cost_per_unit': round(cost / qty, 4),
                                'total_units': qty,
                                'leftover': 0,
                                'combined_score': round(score, 1)
                            })
        
        # 3-box combinations (limited search, all different SKUs)
        for i, b1 in enumerate(top_boxes[:8]):
            for j, b2 in enumerate(top_boxes[i+1:8], i+1):
                if b1.sku == b2.sku:
                    continue
                for b3 in top_boxes[j+1:8]:
                    if b3.sku == b1.sku or b3.sku == b2.sku:
                        continue
                    max_n1 = min(qty // b1.units_per_box, 10)
                    for n1 in range(1, max_n1 + 1):
                        rem1 = qty - n1 * b1.units_per_box
                        if rem1 <= 0:
                            continue
                        max_n2 = min(rem1 // b2.units_per_box, 10)
                        for n2 in range(1, max_n2 + 1):
                            rem2 = rem1 - n2 * b2.units_per_box
                            if rem2 <= 0 or rem2 % b3.units_per_box != 0:
                                continue
                            n3 = rem2 // b3.units_per_box
                            if n3 > 0 and n3 <= 10:
                                total = n1 + n2 + n3
                                score = (b1.overall_score * n1 + b2.overall_score * n2 + b3.overall_score * n3) / total
                                cost = round(n1 * b1.price + n2 * b2.price + n3 * b3.price, 2)
                                
                                combinations.append({
                                    'type': '3-box mix',
                                    'boxes': [
                                        self._box_to_dict(b1, n1, n1 * b1.units_per_box),
                                        self._box_to_dict(b2, n2, n2 * b2.units_per_box),
                                        self._box_to_dict(b3, n3, n3 * b3.units_per_box)
                                    ],
                                    'total_boxes': total,
                                    'total_cost': cost,
                                    'cost_per_unit': round(cost / qty, 4),
                                    'total_units': qty,
                                    'leftover': 0,
                                    'combined_score': round(score, 1)
                                })
        
        # Sort by best score, then lowest cost
        combinations.sort(key=lambda c: (-c['combined_score'], c['total_cost']))
        
        # Deduplicate by total units per SKU
        seen = set()
        unique = []
        for c in combinations:
            sku_totals = {}
            for b in c['boxes']:
                sku_totals[b['sku']] = sku_totals.get(b['sku'], 0) + b['count']
            key = tuple(sorted(sku_totals.items()))
            if key not in seen:
                seen.add(key)
                unique.append(c)
        
        return unique[:6]
    
    def _box_to_dict(self, config: BoxConfig, count: int, units: int) -> Dict:
        """Convert BoxConfig to dict for response"""
        return {
            'sku': config.sku,
            'dimensions': f"{config.length}\" x {config.width}\" x {config.height}\"",
            'length': config.length,
            'width': config.width,
            'height': config.height,
            'price': config.price,
            'units_per_box': config.units_per_box,
            'arrangement': f"{config.arrangement[0]} x {config.arrangement[1]} x {config.arrangement[2]} layers",
            'orientation': config.orientation,
            'count': count,
            'units_packed': units,
            'subtotal': round(count * config.price, 2),
            'scores': {
                'overall': config.overall_score,
                'pallet': config.pallet_score,
                'volume': config.volume_score,
                'price': config.price_score,
                'ergonomic': config.ergonomic_score
            },
            'metrics': {
                'price_per_unit': config.price_per_unit,
                'volume_utilization': config.volume_utilization,
                'boxes_per_pallet': config.boxes_per_pallet,
                'total_weight': config.total_weight
            }
        }
    
    def _evaluate_box(self, box_l, box_w, box_h, price, sku) -> Optional[BoxConfig]:
        """Evaluate a box for the product"""
        
        # Find best packing orientation
        best_units = 0
        best_arrangement = (0, 0, 0)
        best_orientation = ""
        
        for pl, pw, ph, orient in self._get_orientations():
            if pl > box_l or pw > box_w or ph > box_h:
                continue
            
            along_l = int(box_l / pl)
            along_w = int(box_w / pw)
            layers = int(box_h / ph)
            units = along_l * along_w * layers
            
            if units > best_units:
                best_units = units
                best_arrangement = (along_l, along_w, layers)
                best_orientation = orient
        
        if best_units == 0:
            return None
        
        # Check weight
        box_surface = 2 * (box_l * box_w + box_l * box_h + box_w * box_h)
        box_weight = (box_surface / 144) * 0.6
        product_weight = best_units * self.product.weight
        total_weight = box_weight + product_weight
        
        # Reduce units if overweight
        if total_weight > self.MAX_WEIGHT:
            max_product_weight = self.MAX_WEIGHT - box_weight
            best_units = int(max_product_weight / self.product.weight)
            if best_units <= 0:
                return None
            product_weight = best_units * self.product.weight
            total_weight = box_weight + product_weight
        
        # Calculate metrics
        product_volume = best_units * self.product.volume
        box_volume = box_l * box_w * box_h
        volume_utilization = product_volume / box_volume if box_volume > 0 else 0
        
        price_per_unit = price / best_units if best_units > 0 else 999
        
        # Calculate pallet fit
        boxes_per_pallet = self._calculate_pallet_fit(box_l, box_w, box_h)
        
        # Limited mode calculations
        boxes_needed = 0
        total_units = 0
        leftover = 0
        
        if self.is_limited:
            boxes_needed = math.ceil(self.product.quantity / best_units)
            total_units = boxes_needed * best_units
            leftover = total_units - self.product.quantity
        
        # Warnings
        warnings = []
        if total_weight > self.WARNING_WEIGHT:
            warnings.append(f"Heavy: {total_weight:.1f} lbs")
        
        dims = sorted([box_l, box_w, box_h], reverse=True)
        if dims[0] > 36:
            warnings.append("Exceeds 36\" limit")
            return None
        if dims[1] > 25 or dims[2] > 25:
            warnings.append("Exceeds 25\" limit")
            return None
        
        # Raw scores (will be normalized later)
        pallet_score_raw = boxes_per_pallet
        volume_score_raw = volume_utilization
        price_score_raw = 1 / price_per_unit if price_per_unit > 0 else 0
        ergonomic_score_raw = self._calculate_ergonomic_score(box_l, box_w, box_h, total_weight)
        
        return BoxConfig(
            sku=sku,
            length=box_l,
            width=box_w,
            height=box_h,
            price=price,
            units_per_box=best_units,
            arrangement=best_arrangement,
            orientation=best_orientation,
            boxes_needed=boxes_needed,
            total_units=total_units,
            leftover=leftover,
            pallet_score=pallet_score_raw,
            volume_score=volume_score_raw,
            price_score=price_score_raw,
            ergonomic_score=ergonomic_score_raw,
            price_per_unit=round(price_per_unit, 4),
            volume_utilization=round(volume_utilization * 100, 1),
            boxes_per_pallet=boxes_per_pallet,
            total_weight=round(total_weight, 2),
            warnings=warnings or []
        )
    
    def _get_orientations(self):
        """Get all 6 product orientations"""
        l, w, h = self.product.length, self.product.width, self.product.height
        orients = [
            (l, w, h, "Original"),
            (l, h, w, "Rotated A"),
            (w, l, h, "Rotated B"),
            (w, h, l, "Rotated C"),
            (h, l, w, "Rotated D"),
            (h, w, l, "Rotated E"),
        ]
        
        seen = set()
        unique = []
        for pl, pw, ph, name in orients:
            key = (round(pl, 2), round(pw, 2), round(ph, 2))
            if key not in seen:
                seen.add(key)
                unique.append((pl, pw, ph, name))
        return unique
    
    def _calculate_pallet_fit(self, box_l, box_w, box_h):
        """Calculate how many boxes fit on a pallet"""
        best_fit = 0
        
        # Try both orientations on pallet
        for bl, bw, bh in [(box_l, box_w, box_h), (box_w, box_l, box_h)]:
            along_length = int(PALLET_LENGTH / bl)
            along_width = int(PALLET_WIDTH / bw)
            layers = int(PALLET_HEIGHT / bh)
            
            fit = along_length * along_width * layers
            best_fit = max(best_fit, fit)
        
        return best_fit
    
    def _calculate_ergonomic_score(self, box_l, box_w, box_h, weight):
        """Calculate ergonomic score (higher = easier to handle)"""
        # Ideal: small box, light weight, cube-shaped
        
        # Size penalty (larger = worse)
        max_dim = max(box_l, box_w, box_h)
        size_score = max(0, 100 - max_dim * 2)
        
        # Weight penalty (heavier = worse)
        weight_score = max(0, 100 - weight * 2.5)
        
        # Shape penalty (less cubic = worse for handling)
        dims = sorted([box_l, box_w, box_h])
        ratio = dims[0] / dims[2] if dims[2] > 0 else 0
        shape_score = ratio * 100
        
        return (size_score * 0.4 + weight_score * 0.4 + shape_score * 0.2)
    
    def _normalize_scores(self, configs: List[BoxConfig]):
        """Normalize all scores to 1-100 scale"""
        if not configs:
            return
        
        # Find min/max for each metric
        metrics = ['pallet_score', 'volume_score', 'price_score', 'ergonomic_score']
        
        for metric in metrics:
            values = [getattr(c, metric) for c in configs]
            min_val = min(values)
            max_val = max(values)
            range_val = max_val - min_val if max_val != min_val else 1
            
            for c in configs:
                raw = getattr(c, metric)
                normalized = ((raw - min_val) / range_val) * 99 + 1  # 1-100
                setattr(c, metric, round(normalized, 1))
        
        # Calculate overall score (weighted average)
        for c in configs:
            c.overall_score = round(
                c.pallet_score * 0.30 +
                c.volume_score * 0.25 +
                c.price_score * 0.25 +
                c.ergonomic_score * 0.20,
                1
            )


# =============================================================================
# HTTP SERVER
# =============================================================================

class Handler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}", flush=True)
    
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _error(self, msg, code=400):
        self._json({'error': msg}, code)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()
    
    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/':
            path = '/master_case_optimizer.html'
        
        filepath = path.lstrip('/')
        if '..' in filepath:
            self._error('Invalid', 403)
            return
        
        MIME_TYPES = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
        }
        
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            ext = '.' + filepath.rsplit('.', 1)[-1] if '.' in filepath else ''
            content_type = MIME_TYPES.get(ext.lower(), 'application/octet-stream')
            self.send_header('Content-Type', content_type)
            self._cors()
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self._error('Not found', 404)
    
    def do_POST(self):
        print(f"\n>>> POST {self.path}", flush=True)
        
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body.decode()) if body else {}
        except:
            self._error('Invalid JSON')
            return
        
        if self.path == '/api/optimize':
            self._handle_optimize(data)
        elif self.path == '/api/boxes':
            self._handle_boxes()
        else:
            self._error('Unknown endpoint', 404)
    
    def _handle_optimize(self, data):
        try:
            product = Product(
                name=data.get('name', 'Product'),
                length=float(data.get('length', 0)),
                width=float(data.get('width', 0)),
                height=float(data.get('height', 0)),
                weight=float(data.get('weight', 0)),
                quantity=int(data.get('quantity', -1))
            )
            
            limited_mode = data.get('limited_mode', 'case_packed')
            
            # Advanced cost assumptions (optional)
            cost_opts = {
                'label_per_box': max(0, float(data.get('label_per_box', 0) or 0)),
                'handling_per_box': max(0, float(data.get('handling_per_box', 0.25) or 0.25)),
                'labor_hourly': float(data.get('labor_hourly')) if data.get('labor_hourly') not in (None, '') else None,
                'boxes_per_hour': float(data.get('boxes_per_hour')) if data.get('boxes_per_hour') not in (None, '') else None,
                'fba_placement': data.get('fba_placement', '5+') or '5+',
                'fba_schedule_2026': data.get('fba_schedule_2026') in (True, 'true', '2026', 1),
            }
            if cost_opts['fba_placement'] not in ('single', '2-3', '5+'):
                cost_opts['fba_placement'] = '5+'
            
            if product.length <= 0 or product.width <= 0 or product.height <= 0:
                self._error('Invalid dimensions')
                return
            
            if product.weight <= 0:
                self._error('Invalid weight')
                return
            
            print(f">>> Product: {product.length}x{product.width}x{product.height}, {product.weight}lb, qty={product.quantity}, mode={limited_mode}", flush=True)
            
            optimizer = MasterCaseOptimizer(product, limited_mode)
            
            def add_breakdown(total_boxes: int, total_units: int, box_cost_total: float) -> Dict:
                return compute_cost_breakdown(
                    product, total_boxes, total_units, box_cost_total,
                    label_per_box=cost_opts['label_per_box'],
                    handling_per_box=cost_opts['handling_per_box'],
                    labor_hourly=cost_opts['labor_hourly'],
                    boxes_per_hour=cost_opts['boxes_per_hour'],
                    fba_placement=cost_opts['fba_placement'],
                    fba_schedule_2026=cost_opts['fba_schedule_2026'],
                )
            
            response = {
                'product': {
                    'name': product.name,
                    'dimensions': f"{product.length}\" x {product.width}\" x {product.height}\"",
                    'weight': product.weight,
                    'quantity': product.quantity,
                    'mode': 'unlimited' if product.quantity <= 0 else limited_mode
                },
                'pallet': {
                    'length': PALLET_LENGTH,
                    'width': PALLET_WIDTH,
                    'height': PALLET_HEIGHT
                },
                'cost_assumptions': cost_opts,
            }
            
            if product.quantity <= 0:
                # Unlimited mode: total_units and total_boxes are per "run" - use 1 box for per-unit display
                results = optimizer.optimize()
                response['recommendations'] = []
                
                for idx, c in enumerate(results):
                    total_boxes_here = 1
                    total_units_here = c.units_per_box
                    box_cost_here = c.price
                    rec = {
                        'rank': idx + 1,
                        'sku': c.sku,
                        'dimensions': f"{c.length}\" x {c.width}\" x {c.height}\"",
                        'length': c.length,
                        'width': c.width,
                        'height': c.height,
                        'price': c.price,
                        'units_per_box': c.units_per_box,
                        'arrangement': f"{c.arrangement[0]} x {c.arrangement[1]} x {c.arrangement[2]} layers",
                        'orientation': c.orientation,
                        'scores': {
                            'overall': c.overall_score,
                            'pallet': c.pallet_score,
                            'volume': c.volume_score,
                            'price': c.price_score,
                            'ergonomic': c.ergonomic_score
                        },
                        'metrics': {
                            'price_per_unit': c.price_per_unit,
                            'volume_utilization': c.volume_utilization,
                            'boxes_per_pallet': c.boxes_per_pallet,
                            'total_weight': c.total_weight
                        },
                        'warnings': c.warnings,
                        'cost_breakdown': add_breakdown(total_boxes_here, total_units_here, box_cost_here),
                    }
                    response['recommendations'].append(rec)
                
                print(f">>> Found {len(results)} options (unlimited)", flush=True)
            
            elif limited_mode == 'case_packed':
                result = optimizer.optimize_case_packed()
                for combo in result['combinations']:
                    combo['cost_breakdown'] = add_breakdown(
                        combo['total_boxes'], combo['total_units'], combo['total_cost']
                    )
                response['combinations'] = result['combinations']
                response['suggested_quantities'] = result['suggested_quantities']
                print(f">>> Found {len(result['combinations'])} case-packed perfect fits", flush=True)
                if result['suggested_quantities']:
                    print(f">>> Suggested quantities: {result['suggested_quantities']}", flush=True)
            
            else:
                combos = optimizer.optimize_single_units()
                for combo in combos:
                    combo['cost_breakdown'] = add_breakdown(
                        combo['total_boxes'], combo['total_units'], combo['total_cost']
                    )
                response['combinations'] = combos
                print(f">>> Found {len(combos)} single-units combinations", flush=True)
            
            self._json(response)
            
        except Exception as e:
            import traceback
            print(f">>> ERROR: {e}\n{traceback.format_exc()}", flush=True)
            self._error(str(e))
    
    def _handle_boxes(self):
        boxes = []
        for l, w, h, price, sku in ULINE_BOXES:
            boxes.append({
                'sku': sku,
                'dimensions': f"{l}\" x {w}\" x {h}\"",
                'price': price
            })
        self._json({'boxes': boxes})


# =============================================================================
# MAIN
# =============================================================================

def main():
    port = 8002
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 60, flush=True)
    print("  MASTER CASE OPTIMIZER v2.0", flush=True)
    print("=" * 60, flush=True)
    
    try:
        server = HTTPServer(('', port), Handler)
        print(f"\n  http://localhost:{port}", flush=True)
        print(f"\n  Ctrl+C to stop", flush=True)
        print("=" * 60, flush=True)
        
        import webbrowser
        webbrowser.open(f'http://localhost:{port}')
        
        server.serve_forever()
    except OSError:
        print(f"\nERROR: Port {port} in use!", flush=True)
        input("Press Enter...")
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)


if __name__ == '__main__':
    main()
