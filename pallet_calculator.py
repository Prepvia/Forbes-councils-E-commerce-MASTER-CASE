"""
3D Pallet Calculator using 1" cube grid system
==============================================
Uses 1" x 1" x 1" cubes to track available space
Pallet: 40" x 48" base, 65" max height, 1400 lbs max weight
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import json


@dataclass
class Box:
    """Box definition"""
    name: str
    length: float  # inches
    width: float   # inches
    height: float  # inches
    weight: float  # lbs
    quantity: int
    color: str = "#2196F3"


@dataclass
class BoxPlacement:
    """Box placement in 3D space"""
    box: Box
    x: float  # Position along length (0-48")
    y: float  # Position along width (0-40")
    z: float  # Height above pallet base
    length: float
    width: float
    height: float
    orientation: str = "Original"  # Which face is on top: "Original", "Length-Rotated", "Width-Rotated", etc.
    original_dimensions: Tuple[float, float, float] = None  # (length, width, height) - original box dimensions


@dataclass
class Layer:
    """A single layer of boxes"""
    boxes: List[BoxPlacement]
    height: float  # Height of this layer
    weight: float  # Total weight of this layer


@dataclass
class Pallet:
    """Complete pallet configuration"""
    layers: List[Layer]
    total_boxes: int
    total_height: float
    total_weight: float


class PalletCalculator:
    """Calculate pallet arrangements using 1" cube grid"""
    
    PALLET_LENGTH = 48  # inches
    PALLET_WIDTH = 40   # inches
    PALLET_BASE_HEIGHT = 6  # inches (pallet base)
    MAX_HEIGHT = 65     # inches (total including base)
    MAX_WEIGHT = 1400    # lbs
    CUBE_SIZE = 1        # 1 inch cubes
    
    def __init__(self):
        # Usable area (accounting for margins)
        self.usable_length = self.PALLET_LENGTH
        self.usable_width = self.PALLET_WIDTH
        self.usable_height = self.MAX_HEIGHT - self.PALLET_BASE_HEIGHT  # 59 inches
        
        # Grid dimensions (in cubes)
        self.grid_x = int(self.usable_length)  # 48 cubes
        self.grid_y = int(self.usable_width)   # 40 cubes
        self.grid_z = int(self.usable_height)  # 59 cubes
        
    def calculate_pallets(self, boxes: List[Box]) -> List[Pallet]:
        """
        Calculate how many pallets are needed for given boxes
        Returns list of Pallet objects
        """
        pallets = []
        remaining_boxes = self._expand_boxes(boxes)  # Convert to individual boxes
        
        while remaining_boxes:
            pallet, remaining = self._pack_pallet(remaining_boxes)
            if pallet and pallet.total_boxes > 0:
                pallets.append(pallet)
                remaining_boxes = remaining
            else:
                # Can't pack any more boxes
                break
        
        return pallets
    
    def _expand_boxes(self, boxes: List[Box]) -> List[Box]:
        """Expand boxes by quantity into individual items"""
        expanded = []
        for box in boxes:
            for _ in range(box.quantity):
                expanded.append(Box(
                    name=box.name,
                    length=box.length,
                    width=box.width,
                    height=box.height,
                    weight=box.weight,
                    quantity=1,
                    color=box.color
                ))
        return expanded
    
    def _pack_pallet(self, boxes: List[Box]) -> Tuple[Optional[Pallet], List[Box]]:
        """
        Pack boxes into a single pallet using 1" cube grid
        Returns: (Pallet, remaining_boxes)
        """
        # Initialize 3D grid: grid[x][y][z] = True if occupied
        grid = [[[False for _ in range(self.grid_z)] 
                 for _ in range(self.grid_y)] 
                 for _ in range(self.grid_x)]
        
        # Height map: height_map[x][y] = current height at position (x, y)
        height_map = [[0 for _ in range(self.grid_y)] 
                      for _ in range(self.grid_x)]
        
        placements = []
        total_weight = 0.0
        remaining = []
        
        # Sort boxes by volume (largest first) - First Fit Decreasing
        # But also consider trying smaller boxes first if they fit better
        sorted_boxes = sorted(boxes, key=lambda b: (-b.length * b.width * b.height, -b.weight))
        
        # Try multiple passes to fill gaps around large boxes
        max_passes = 3
        pass_num = 0
        boxes_to_try = sorted_boxes.copy()
        
        while pass_num < max_passes and boxes_to_try:
            boxes_placed_this_pass = 0
            boxes_remaining_this_pass = []
            
            for box in boxes_to_try:
                # Try all 6 orientations and find the BEST one (not just first that fits)
                orientations = self._get_orientations(box)
                orientation_names = self._get_orientation_names(box)
                
                best_placement = None
                best_score = float('inf')
                best_orient_idx = -1
                
                # Test ALL orientations and find the best one
                for idx, orient in enumerate(orientations):
                    ol, ow, oh = orient
                    orient_name = orientation_names[idx]
                    
                    # Convert to grid coordinates (round to nearest cube)
                    grid_l = max(1, int(round(ol)))
                    grid_w = max(1, int(round(ow)))
                    grid_h = max(1, int(round(oh)))
                    
                    # Find best position for this orientation
                    best_pos = self._find_best_position_with_score(
                        grid, height_map, grid_l, grid_w, grid_h, 
                        total_weight + box.weight
                    )
                    
                    if best_pos:
                        pos, score = best_pos
                        gx, gy, gz = pos
                        
                        # Score: lower is better (prefer lower height, then better space utilization)
                        # Add bonus for orientations that use less vertical space (prefer wider/shorter)
                        # This helps fill gaps around large boxes
                        height_penalty = grid_h * 1000  # Prefer shorter heights
                        score_with_penalty = score + height_penalty
                        
                        if score_with_penalty < best_score:
                            best_score = score_with_penalty
                            best_orient_idx = idx
                            best_placement = {
                                'pos': (gx, gy, gz),
                                'orient': orient,
                                'orient_name': orient_name,
                                'grid_l': grid_l,
                                'grid_w': grid_w,
                                'grid_h': grid_h
                            }
                
                # Place the best orientation found
                if best_placement:
                    gx, gy, gz = best_placement['pos']
                    ol, ow, oh = best_placement['orient']
                    
                    # Log if rotation was used (not original)
                    original_orient = (box.length, box.width, box.height)
                    if best_placement['orient'] != original_orient:
                        print(f"[ROTATION] {box.name}: Rotated from {box.length}\"×{box.width}\"×{box.height}\" to {ol}\"×{ow}\"×{oh}\" ({best_placement['orient_name']})")
                    
                    # Place box
                    self._place_box_in_grid(
                        grid, height_map, gx, gy, gz, 
                        best_placement['grid_l'], 
                        best_placement['grid_w'], 
                        best_placement['grid_h']
                    )
                    
                    # Convert grid position back to inches
                    real_x = gx * self.CUBE_SIZE
                    real_y = gy * self.CUBE_SIZE
                    real_z = gz * self.CUBE_SIZE
                    
                    placement = BoxPlacement(
                        box=box,
                        x=real_x,
                        y=real_y,
                        z=real_z,
                        length=ol,
                        width=ow,
                        height=oh,
                        orientation=best_placement['orient_name'],
                        original_dimensions=(box.length, box.width, box.height)
                    )
                    placements.append(placement)
                    total_weight += box.weight
                    boxes_placed_this_pass += 1
                    # Don't try this box again
                else:
                    # Keep in list for next pass if it didn't fit
                    boxes_remaining_this_pass.append(box)
            
            # Update list for next pass
            boxes_to_try = boxes_remaining_this_pass
            
            # If no boxes were placed this pass, stop trying
            if boxes_placed_this_pass == 0:
                break
            
            pass_num += 1
        
        # Any remaining boxes go to remaining list
        remaining.extend(boxes_to_try)
        
        if not placements:
            return None, boxes
        
        # Group placements into layers
        layers = self._group_into_layers(placements)
        
        max_height = max((p.z + p.height for p in placements), default=0)
        
        pallet = Pallet(
            layers=layers,
            total_boxes=len(placements),
            total_height=max_height + self.PALLET_BASE_HEIGHT,
            total_weight=total_weight
        )
        
        return pallet, remaining
    
    def _get_orientations(self, box: Box) -> List[Tuple[float, float, float]]:
        """Get all 6 possible orientations of a box"""
        l, w, h = box.length, box.width, box.height
        orientations = [
            (l, w, h),  # Original: length×width face on bottom, height up
            (l, h, w),  # Rotated: length×height face on bottom, width up
            (w, l, h),  # Rotated: width×length face on bottom, height up
            (w, h, l),  # Rotated: width×height face on bottom, length up
            (h, l, w),  # Rotated: height×length face on bottom, width up
            (h, w, l),  # Rotated: height×width face on bottom, length up
        ]
        # Remove duplicates
        unique = []
        seen = set()
        for orient in orientations:
            if orient not in seen:
                seen.add(orient)
                unique.append(orient)
        return unique
    
    def _get_orientation_names(self, box: Box) -> List[str]:
        """Get descriptive names for each orientation"""
        l, w, h = box.length, box.width, box.height
        orientations = [
            (l, w, h),
            (l, h, w),
            (w, l, h),
            (w, h, l),
            (h, l, w),
            (h, w, l),
        ]
        
        names = []
        for ol, ow, oh in orientations:
            if (ol, ow, oh) == (l, w, h):
                names.append("Original (Height up)")
            elif (ol, ow, oh) == (l, h, w):
                names.append("Width up (rotated)")
            elif (ol, ow, oh) == (w, l, h):
                names.append("Height up (rotated)")
            elif (ol, ow, oh) == (w, h, l):
                names.append("Length up (rotated)")
            elif (ol, ow, oh) == (h, l, w):
                names.append("Width up (rotated)")
            elif (ol, ow, oh) == (h, w, l):
                names.append("Length up (rotated)")
            else:
                names.append(f"{ol}\"×{ow}\" base, {oh}\" up")
        
        # Remove duplicates matching orientations
        unique_names = []
        seen_orientations = set()
        for i, orient in enumerate(orientations):
            if orient not in seen_orientations:
                seen_orientations.add(orient)
                unique_names.append(names[i])
        
        return unique_names
    
    def _find_best_position(
        self, grid: List[List[List[bool]]], 
        height_map: List[List[int]],
        grid_l: int, grid_w: int, grid_h: int,
        total_weight: float
    ) -> Optional[Tuple[int, int, int]]:
        """
        Find best position for box using 1" cube grid
        Returns: (grid_x, grid_y, grid_z) or None
        """
        result = self._find_best_position_with_score(grid, height_map, grid_l, grid_w, grid_h, total_weight)
        if result:
            return result[0]  # Return just the position
        return None
    
    def _find_best_position_with_score(
        self, grid: List[List[List[bool]]], 
        height_map: List[List[int]],
        grid_l: int, grid_w: int, grid_h: int,
        total_weight: float
    ) -> Optional[Tuple[Tuple[int, int, int], float]]:
        """
        Find best position for box using 1" cube grid with score
        Returns: ((grid_x, grid_y, grid_z), score) or None
        Score: lower is better (prefers lower height, better space utilization)
        """
        if total_weight > self.MAX_WEIGHT:
            return None
        
        best_pos = None
        best_score = float('inf')
        
        # Try all possible positions
        for gx in range(self.grid_x - grid_l + 1):
            for gy in range(self.grid_y - grid_w + 1):
                # Get current height at this position (check all base positions)
                base_height = 0
                for x in range(gx, gx + grid_l):
                    for y in range(gy, gy + grid_w):
                        base_height = max(base_height, height_map[x][y])
                
                # Check if box fits in height
                if base_height + grid_h > self.grid_z:
                    continue
                
                gz = base_height
                
                # Check if all cubes are free
                if self._can_place_at(grid, gx, gy, gz, grid_l, grid_w, grid_h):
                    # Score: prefer lower height (most important), then better position
                    # Lower height = lower score (better)
                    # Also prefer positions that leave less wasted space
                    score = gz * 1000000 + gy * 1000 + gx
                    if score < best_score:
                        best_score = score
                        best_pos = (gx, gy, gz)
        
        if best_pos:
            return (best_pos, best_score)
        return None
    
    def _can_place_at(
        self, grid: List[List[List[bool]]],
        gx: int, gy: int, gz: int,
        grid_l: int, grid_w: int, grid_h: int
    ) -> bool:
        """Check if box can be placed at grid position"""
        # Check bounds
        if gx < 0 or gx + grid_l > self.grid_x:
            return False
        if gy < 0 or gy + grid_w > self.grid_y:
            return False
        if gz < 0 or gz + grid_h > self.grid_z:
            return False
        
        # Check if all cubes are free
        for x in range(gx, gx + grid_l):
            for y in range(gy, gy + grid_w):
                # Check if base is supported (must be on ground or on top of other boxes)
                # The base height should match the height_map
                for z in range(gz, gz + grid_h):
                    if grid[x][y][z]:
                        return False
        
        return True
    
    def _place_box_in_grid(
        self, grid: List[List[List[bool]]],
        height_map: List[List[int]],
        gx: int, gy: int, gz: int,
        grid_l: int, grid_w: int, grid_h: int
    ):
        """Mark cubes as occupied in grid"""
        for x in range(gx, gx + grid_l):
            for y in range(gy, gy + grid_w):
                for z in range(gz, gz + grid_h):
                    grid[x][y][z] = True
                # Update height map
                height_map[x][y] = gz + grid_h
    
    def _group_into_layers(self, placements: List[BoxPlacement]) -> List[Layer]:
        """Group placements by their base height to create layers"""
        # Group by z coordinate (rounded to nearest inch)
        layers_dict = {}
        
        for placement in placements:
            z_key = int(round(placement.z))
            if z_key not in layers_dict:
                layers_dict[z_key] = []
            layers_dict[z_key].append(placement)
        
        # Create Layer objects - keep original z values from grid
        layers = []
        for z in sorted(layers_dict.keys()):
            layer_placements = layers_dict[z]
            layer_height = max((p.height for p in layer_placements), default=0)
            layer_weight = sum((p.box.weight for p in layer_placements))
            
            layer = Layer(
                boxes=layer_placements,
                height=layer_height,
                weight=layer_weight
            )
            layers.append(layer)
        
        return layers


# Web server
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse


class PalletHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/calculate':
            try:
                print(f"[DEBUG] Received POST request to /api/calculate")
                content_length = int(self.headers.get('Content-Length', 0))
                
                if content_length == 0:
                    self._send_error('Empty request body')
                    return
                
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                boxes_data = request_data.get('boxes', [])
                print(f"[DEBUG] Received {len(boxes_data)} box types")
                
                if not boxes_data:
                    self._send_error('No boxes provided')
                    return
                
                # Convert to Box objects
                boxes = []
                for b in boxes_data:
                    try:
                        boxes.append(Box(
                            name=b['name'],
                            length=float(b['length']),
                            width=float(b['width']),
                            height=float(b['height']),
                            weight=float(b['weight']),
                            quantity=int(b['quantity']),
                            color=b.get('color', '#2196F3')
                        ))
                    except Exception as e:
                        print(f"[ERROR] Failed to parse box: {b}, error: {e}")
                        continue
                
                if not boxes:
                    self._send_error('No valid boxes provided')
                    return
                
                print(f"[DEBUG] Processing {len(boxes)} box types...")
                
                # Calculate pallets
                calculator = PalletCalculator()
                pallets = calculator.calculate_pallets(boxes)
                
                print(f"[DEBUG] Generated {len(pallets)} pallet(s)")
                
                # Convert to JSON
                result = {
                    'pallets': []
                }
                
                for pallet in pallets:
                    pallet_json = {
                        'total_boxes': pallet.total_boxes,
                        'total_height': pallet.total_height,
                        'total_weight': pallet.total_weight,
                        'layers': []
                    }
                    
                    for layer in pallet.layers:
                        layer_json = {
                            'height': layer.height,
                            'weight': layer.weight,
                            'boxes': []
                        }
                        
                        for placement in layer.boxes:
                            box_json = {
                                'name': placement.box.name,
                                'x': placement.x,
                                'y': placement.y,
                                'z': placement.z,
                                'length': placement.length,
                                'width': placement.width,
                                'height': placement.height,
                                'weight': placement.box.weight,
                                'color': placement.box.color,
                                'orientation': placement.orientation,
                                'original_length': placement.original_dimensions[0] if placement.original_dimensions else placement.box.length,
                                'original_width': placement.original_dimensions[1] if placement.original_dimensions else placement.box.width,
                                'original_height': placement.original_dimensions[2] if placement.original_dimensions else placement.box.height
                            }
                            layer_json['boxes'].append(box_json)
                        
                        pallet_json['layers'].append(layer_json)
                    
                    result['pallets'].append(pallet_json)
                
                print(f"[DEBUG] Sending response with {len(result['pallets'])} pallets")
                self._send_json(result)
                
            except Exception as e:
                import traceback
                error_msg = str(e) + '\n' + traceback.format_exc()
                print(f"[ERROR] Exception in /api/calculate: {error_msg}")
                self._send_error(error_msg)
        
        else:
            print(f"[DEBUG] Unknown POST endpoint: {self.path}")
            self._send_error('Unknown endpoint: ' + self.path)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/pallet_3d.html'
        
        try:
            with open(self.path[1:], 'rb') as f:
                content = f.read()
                self.send_response(200)
                
                if self.path.endswith('.html'):
                    self.send_header('Content-type', 'text/html')
                elif self.path.endswith('.js'):
                    self.send_header('Content-type', 'application/javascript')
                elif self.path.endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self._send_error('File not found', 404)
        except Exception as e:
            self._send_error(str(e), 500)
    
    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, message, code=400):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())
    
    def log_message(self, format, *args):
        pass  # Suppress logging


def start_server(port=8000):
    import socket
    
    # Check if port is already in use
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('', port))
        sock.close()
    except OSError:
        print("=" * 70)
        print("  ERROR: PORT 8000 IS ALREADY IN USE!")
        print("=" * 70)
        print(f"\n  Another program is using port {port}.")
        print("  Please:")
        print("  1. Close other programs using port 8000")
        print("  2. Or kill any existing Python processes")
        print("  3. Then try again")
        print("=" * 70)
        input("\n  Press Enter to exit...")
        return
    
    server_address = ('', port)
    try:
        httpd = HTTPServer(server_address, PalletHandler)
    except Exception as e:
        print("=" * 70)
        print("  ERROR: FAILED TO START SERVER!")
        print("=" * 70)
        print(f"\n  Error: {str(e)}")
        print("=" * 70)
        input("\n  Press Enter to exit...")
        return
    
    print("=" * 70)
    print("  3D PALLET STACKER - SERVER STARTED")
    print("=" * 70)
    print(f"\n  ✅ Server running at: http://localhost:{port}")
    print(f"  ✅ Open: http://localhost:{port}/pallet_3d.html")
    print("\n  Press Ctrl+C to stop the server")
    print("=" * 70)
    print("\n  Waiting for requests...")
    print("  (You should see requests when you click 'Calculate Pallets')\n")
    
    # Try to open browser
    try:
        import webbrowser
        webbrowser.open(f'http://localhost:{port}/pallet_3d.html')
    except:
        pass
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n  Server stopped.")
        httpd.server_close()


if __name__ == '__main__':
    start_server()

