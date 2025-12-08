# 3D Pallet Stacker - New Implementation

## Overview
A clean, from-scratch 3D pallet stacking calculator that uses a 1" cube grid system to optimize box placement on pallets.

## Features
- ✅ **1" Cube Grid System**: Uses 1" x 1" x 1" cubes to track available space
- ✅ **Pallet Constraints**: 
  - Base: 40" x 48" inches
  - Max Height: 65 inches (including 6" pallet base)
  - Max Weight: 1400 lbs per pallet
- ✅ **Box Management**: 
  - Name, dimensions (length × width × height), weight, quantity
  - Custom colors for each box type
- ✅ **Step-by-Step Visualization**: See which boxes to add in each layer
- ✅ **CSV Import**: Import box data from Excel/CSV files
- ✅ **Multiple Pallets**: Automatically calculates how many pallets are needed
- ✅ **3D Visualization**: Interactive 3D view with mouse controls

## How to Use

### 1. Start the Server
Double-click `START_PALLET_STACKER.bat` or run:
```bash
python pallet_calculator.py
```

The server will start on `http://localhost:8000`

### 2. Open the Application
Open your browser and go to:
```
http://localhost:8000/pallet_3d.html
```

### 3. Add Boxes
- Enter box name, dimensions (length × width × height in inches), weight (lbs), quantity, and choose a color
- Click "Add Box" to add it to your list
- Repeat for all box types

### 4. Import from CSV (Optional)
Click "Click to import CSV/Excel" and select your file.

CSV Format:
```
Name, Length, Width, Height, Weight, Quantity, Color
Small Box, 12, 10, 8, 20, 50, #2196F3
Large Box, 24, 20, 16, 50, 30, #4CAF50
```

### 5. Calculate Pallets
Click "🚀 Calculate Pallets" to:
- Calculate optimal box placement using 1" cube grid
- Determine how many pallets are needed
- Generate step-by-step building instructions

### 6. View Results
- **Left Panel**: Your box list
- **Center**: 3D visualization of pallets
- **Right Panel**: Step-by-step building instructions

### 7. Navigate Steps
- Use "Next →" and "← Previous" buttons to see each layer
- Watch boxes appear in the 3D view as you progress

## 3D View Controls
- **Rotate**: Click and drag with mouse
- **Zoom**: Scroll wheel
- **Views**: Click buttons (3D, Top, Side, Front) for preset views

## Algorithm
The system uses a **1" cube grid** approach:
1. Divides pallet space into 1" × 1" × 1" cubes
2. Tracks which cubes are occupied
3. For each box, tries all 6 possible orientations
4. Finds best position (lowest height, then best fit)
5. Places box and marks cubes as occupied
6. Continues until no more boxes fit or limits reached

## File Structure
- `pallet_3d.html` - Frontend (3D viewer and UI)
- `pallet_calculator.py` - Backend (calculation engine and web server)
- `START_PALLET_STACKER.bat` - Server startup script

## Requirements
- Python 3.6+
- Modern web browser with WebGL support (Chrome, Firefox, Edge)
- Internet connection (for Three.js library)

## Notes
- Box dimensions are in inches
- Weight is in pounds (lbs)
- The system automatically tries all 6 orientations of each box
- Boxes are placed to minimize height and maximize space utilization
- Multiple pallets are created automatically if all boxes don't fit on one

