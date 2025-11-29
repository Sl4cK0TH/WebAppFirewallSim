# WebApp Firewall Simulator - Quick Reference

## 🚀 Quick Start

```bash
cd /home/zor0ark/Documents/WebAppFirewallSimulator
pip install flask flask-socketio
python app.py
# Open http://localhost:5000
```

## 🎯 Key Features Added

### 1. Configuration Panel
- Click "⚙️ Configuration Panel" button to open
- Three tabs: Network Config, Firewall Rules, Save/Load

### 2. Network Configuration
- **Customize IPs**: Change IP addresses for all three zones
- **Set Gateways**: Configure network gateways
- **Define Subnets**: Set subnet masks
- **Apply Live**: Changes take effect immediately

### 3. Firewall Rules Manager
- **Add Rules**: Source → Destination with ALLOW/DROP
- **Specify Ports**: Define protocols and port numbers
- **Delete Rules**: Remove rules with one click
- **View All**: See all active rules organized by direction

### 4. Draggable Terminals
- **Drag Headers**: Click and drag terminal header bars
- **Rearrange Layout**: Position terminals anywhere on screen
- **Visual Feedback**: Terminals show shadow when dragging
- **Look for ⋮⋮**: Drag indicator on headers

### 5. Save/Load System
- **Save Locally**: Store configs in browser localStorage
- **Load Quickly**: Switch between saved configurations
- **Export JSON**: Download configuration files
- **Import JSON**: Upload and apply saved configs

## 📝 Common Commands

```bash
# Test connectivity
ping 10.0.1.10

# Check network configuration
ifconfig

# View firewall rules
firewall show

# Test port connectivity
nc 10.0.1.10 80

# Make HTTP request
curl http://10.0.1.10

# DNS lookup
nslookup example.com

# Trace route
traceroute 8.8.8.8

# Show current zone
whoami

# Clear screen
clear
```

## 🔥 Example Workflows

### Create a Restrictive DMZ
1. Open Config Panel → Firewall Rules
2. Source: outsider, Destination: dmz
3. Add: ALLOW HTTP:80
4. Add: ALLOW HTTPS:443
5. Add: DROP (no protocol)
6. Test from Outsider terminal

### Custom Network Setup
1. Open Config Panel → Network Config
2. Change DMZ IP to 172.16.0.10
3. Click "Apply Network Configuration"
4. Update firewall rules for new IP
5. Save as "custom-network"

### Block Everything
1. Config Panel → Firewall Rules
2. For each direction, add: DROP (no protocol)
3. Test - all commands should fail

### Allow Internal Access Only
1. insider → dmz: ALLOW ALL
2. insider → outsider: ALLOW HTTP, ALLOW HTTPS
3. outsider → dmz: DROP
4. outsider → insider: DROP

## 🎨 UI Controls

| Element | Action |
|---------|--------|
| Configuration Button | Toggle config panel |
| Tab Buttons | Switch between config sections |
| Apply Button | Save network changes |
| Add Rule Button | Create new firewall rule |
| Delete Button | Remove specific rule |
| Terminal Headers | Drag to move terminals |
| Save Button | Store configuration |
| Load Dropdown | Select saved config |
| Export Button | Download JSON |
| Import Button | Upload JSON file |

## 🛡️ Default Firewall Rules

```
outsider → dmz:
  - ALLOW HTTP:80
  - ALLOW HTTPS:443
  - DROP ALL

outsider → insider:
  - DROP ALL

dmz → insider:
  - ALLOW DB:3306
  - DROP ALL

insider → dmz:
  - ALLOW ALL

insider → outsider:
  - ALLOW HTTP
  - ALLOW HTTPS
  - ALLOW DNS:53
```

## 📊 Default Network Configuration

| Zone | IP | Gateway | Subnet |
|------|-----|---------|--------|
| Outsider | 203.0.113.50 | 203.0.113.1 | 255.255.255.0 |
| DMZ | 10.0.1.10 | 10.0.1.1 | 255.255.255.0 |
| Insider | 192.168.1.100 | 192.168.1.1 | 255.255.255.0 |

## 💡 Tips & Tricks

1. **Test Before Blocking**: Always test connectivity before adding DROP rules
2. **Order Matters**: Firewall rules are processed in order (top to bottom)
3. **Save Often**: Save your configurations with descriptive names
4. **Export for Backup**: Export important configs as JSON files
5. **Drag Freely**: Arrange terminals for your workflow
6. **Use Shortcuts**: Ctrl+L to clear, Ctrl+C to cancel
7. **Check Rules**: Use `firewall show` to verify active rules

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Terminals not working | Refresh page, check Flask is running |
| Config not saving | Enable localStorage in browser |
| Can't drag terminal | Drag from header, not body |
| Commands blocked | Check firewall rules with `firewall show` |
| Network changes not applying | Click "Apply Network Configuration" |

## 🎓 Learning Path

1. **Start Simple**: Use default configuration, test basic commands
2. **Add Rules**: Create simple ALLOW/DROP rules
3. **Custom Networks**: Change IP addresses and test
4. **Complex Scenarios**: Build multi-layer security rules
5. **Save Configs**: Create different security postures
6. **Share**: Export and share configurations with others

---

**Framework**: Python Flask + Flask-SocketIO + xterm.js
**Status**: ✅ All features implemented and working
