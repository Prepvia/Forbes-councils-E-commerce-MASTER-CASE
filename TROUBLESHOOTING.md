# Troubleshooting - "Error calculating, make sure the server is running on port 8000"

## Quick Fix Steps

### 1. Make sure the server is running
- Double-click `START_PALLET_STACKER.bat`
- You should see: "3D PALLET STACKER - SERVER STARTED"
- Keep this window open!

### 2. Check the browser URL
- Open: `http://localhost:8000/pallet_3d.html`
- NOT: `file:///C:/.../pallet_3d.html` (this won't work!)

### 3. Check if port 8000 is available
If you see "PORT 8000 IS ALREADY IN USE":
- Close any other programs using port 8000
- Or close any other Python servers running
- Then try again

### 4. Check browser console
- Press F12 in your browser
- Go to "Console" tab
- Look for error messages
- Share these errors if you need help

### 5. Test server manually
Open in browser: `http://localhost:8000/`
- Should show the HTML file or a directory listing
- If you see an error, the server isn't running correctly

## Common Issues

### Issue: "Failed to fetch" or "NetworkError"
**Solution:** 
- Make sure `START_PALLET_STACKER.bat` is running
- Check that the server window shows "Server running at: http://localhost:8000"
- Try refreshing the page (F5)

### Issue: "Port 8000 is already in use"
**Solution:**
1. Close the server window (Ctrl+C)
2. Check Task Manager for other Python processes
3. Close any other programs using port 8000
4. Restart the server

### Issue: Server starts but browser can't connect
**Solution:**
- Make sure you're using `http://localhost:8000/pallet_3d.html`
- NOT `file://` protocol
- Try a different browser (Chrome, Firefox, Edge)

### Issue: Python not found
**Solution:**
- Install Python from https://www.python.org/
- Make sure Python is in your PATH
- Restart your computer after installing Python

## Testing the Server

1. Start the server: `START_PALLET_STACKER.bat`
2. Open browser: `http://localhost:8000/pallet_3d.html`
3. Add a test box:
   - Name: "Test Box"
   - Length: 12, Width: 10, Height: 8
   - Weight: 20, Quantity: 1
   - Click "Add Box"
4. Click "Calculate Pallets"
5. You should see pallets appear in the 3D view

## Still Having Issues?

1. Check the server window for error messages
2. Check browser console (F12) for JavaScript errors
3. Make sure Python 3.6+ is installed
4. Try restarting both the server and browser

