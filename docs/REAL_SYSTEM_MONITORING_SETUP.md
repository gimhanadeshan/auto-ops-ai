# Real System Monitoring Setup Guide

## Overview

The system monitoring feature now uses **psutil** to access real Task Manager data (CPU, RAM, Disk usage) from the user's device. This provides accurate, real-time system monitoring similar to Windows Task Manager.

## Installation

### Step 1: Install psutil

```bash
# In your backend virtual environment
pip install psutil==5.9.8

# Or using requirements.txt
pip install -r requirements.txt
```

### Step 2: Verify Installation

```python
# Test psutil import
python -c "import psutil; print('psutil version:', psutil.__version__)"
```

## How It Works

### Backend Endpoint: `/api/monitoring/stats`

Returns real system statistics:
```json
{
  "cpu": 45.2,
  "ram": 62.5,
  "disk": 78.3,
  "network": 12.1,
  "timestamp": "2025-01-27T10:30:00",
  "source": "psutil",
  "details": {
    "cpu_cores": 8,
    "memory_total_gb": 16.0,
    "memory_used_gb": 10.0,
    "memory_available_gb": 6.0,
    "disk_total_gb": 500.0,
    "disk_used_gb": 390.0,
    "disk_free_gb": 110.0
  }
}
```

### Frontend Integration

1. **Permission Request**: User must grant permission before accessing system data
2. **Real-time Polling**: Frontend polls `/api/monitoring/stats` every 1 second
3. **Fallback**: If psutil unavailable, falls back to simulated data

## Permission Flow

1. User visits System Monitoring page
2. Permission modal appears automatically
3. User reads about what data will be accessed
4. User checks "I understand" checkbox
5. User clicks "Grant Access"
6. System starts fetching real data

## Security & Privacy

- ✅ **User Consent Required**: Permission modal before accessing data
- ✅ **Local Only**: Data never leaves user's machine
- ✅ **No Storage**: System stats are not stored or logged
- ✅ **Transparent**: Clear explanation of what's accessed

## Platform Support

### Windows
- ✅ Full support for CPU, RAM, Disk
- ✅ Uses `C:\` drive for disk stats

### macOS
- ✅ Full support for CPU, RAM, Disk
- ✅ Uses `/` root partition

### Linux
- ✅ Full support for CPU, RAM, Disk
- ✅ Uses `/` root partition

## Troubleshooting

### psutil Not Available

**Error**: `psutil not available`

**Solution**:
```bash
pip install psutil
```

### Permission Denied

**Error**: `Permission denied` when accessing disk

**Solution**: 
- Run backend with appropriate permissions
- On Linux/Mac, may need sudo for some disk operations

### Data Not Updating

**Check**:
1. Backend is running
2. psutil is installed
3. Permission was granted in frontend
4. Check browser console for errors

## API Endpoints

### GET `/api/monitoring/stats`
Real system statistics using psutil

**Response**:
- `cpu`: CPU usage percentage (0-100)
- `ram`: RAM usage percentage (0-100)
- `disk`: Disk usage percentage (0-100)
- `network`: Network activity (0-100, estimated)
- `details`: Detailed system information

### GET `/api/monitoring/metrics`
System metrics (tries real data first, falls back to simulated)

**Response**:
- `metrics`: CPU, Memory, Disk, Network percentages
- `checks`: Array of system checks with status
- `real_data`: Boolean indicating if data is real or simulated

## Code Examples

### Backend (Python)

```python
import psutil

# Get CPU usage
cpu = psutil.cpu_percent(interval=0.5)

# Get memory
memory = psutil.virtual_memory()
ram_percent = memory.percent

# Get disk
disk = psutil.disk_usage('/')
disk_percent = disk.percent
```

### Frontend (JavaScript)

```javascript
// Poll real stats every second
async function pollStats() {
  try {
    const res = await fetch("http://localhost:8000/api/monitoring/stats");
    const data = await res.json();
    
    console.log(`CPU: ${data.cpu}%`);
    console.log(`RAM: ${data.ram}%`);
    console.log(`Disk: ${data.disk}%`);
  } catch (e) {
    console.log("Stats endpoint not available");
  }
}

setInterval(pollStats, 1000);
```

## Testing

### Test Backend Endpoint

```bash
# Test stats endpoint
curl http://localhost:8000/api/monitoring/stats

# Should return JSON with cpu, ram, disk values
```

### Test Frontend

1. Open System Monitoring page
2. Grant permission when modal appears
3. Watch metrics update every second
4. Verify values match Task Manager (Windows) or Activity Monitor (Mac)

## Limitations

- **Browser Security**: Web browsers cannot directly access Task Manager
- **Backend Required**: Must run backend on same machine or have remote access
- **Network Stats**: Network percentage is estimated (not exact)
- **Cross-Platform**: Some metrics may vary by OS

## Future Enhancements

- [ ] Process list (top CPU/memory consumers)
- [ ] Network interface details
- [ ] Disk I/O statistics
- [ ] Temperature monitoring (if available)
- [ ] Historical data tracking

---

**Last Updated**: 2025-01-27  
**Status**: ✅ Implemented and Ready to Use

