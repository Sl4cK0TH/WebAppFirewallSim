# WebApp Firewall Simulator - Testing Guide

## Overview
This guide will help you test the comprehensive logging features of the WebApp Firewall Simulator, including blocked traffic detection, triggered rules, and misconfiguration warnings.

## Setup Instructions

1. **Start the Server**
   ```bash
   cd /home/zor0ark/Documents/WebAppFirewallSimulator
   source .venv/bin/activate
   python app.py
   ```

2. **Open the Simulator**
   - Navigate to: http://localhost:5000
   - You should see 4 terminals: LAN1 (Internal), LAN2 (External), DMZ (Web Server), and Firewall (Admin)
   - The logs panel on the right shows filters and statistics

## Test Scenarios

### Test 1: Basic Network Configuration
Test dynamic IP address and network calculation.

**In LAN1 Terminal (Insider):**
```bash
ifconfig set ip 192.168.10.10
```
- **Expected**: Network should show as `192.168.10.0/24`

**In LAN2 Terminal (Outsider):**
```bash
ifconfig set ip 10.0.0.50
```
- **Expected**: Network should show as `10.0.0.0/24`

**In DMZ Terminal:**
```bash
ifconfig set ip 172.16.0.100
```
- **Expected**: Network should show as `172.16.0.0/24`

---

### Test 2: Block All Incoming Traffic
Test firewall blocking and logging of dropped packets.

**In Firewall Terminal:**
```bash
iptables -A INPUT -j DROP
```

**In LAN2 Terminal (Outsider):**
```bash
nmap 192.168.10.10
```
- **Expected Logs**: Multiple "DROP" entries showing blocked connection attempts
- **Filter Test**: Click "Blocked" button - should show only dropped packets
- **Stats**: "Blocked" counter should increase

---

### Test 3: Allow Specific Port
Test rule-based traffic filtering and allow rules.

**In Firewall Terminal:**
```bash
iptables -F INPUT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -j DROP
```

**In LAN2 Terminal:**
```bash
nmap 192.168.10.10
```
- **Expected Logs**: 
  - "ACCEPT" for port 80
  - "DROP" for all other ports
- **Filter Test**: 
  - Click "Allowed" - should show port 80 accepts
  - Click "Blocked" - should show other ports dropped

---

### Test 4: Detect Rule Conflicts
Test misconfiguration detection with conflicting rules.

**In Firewall Terminal:**
```bash
iptables -F INPUT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j DROP
```
- **Expected Logs**: 
  - WARNING entry: "Conflicting rules detected: Rule X and Rule Y have same conditions but different targets"
- **Filter Test**: Click "Warnings" - should show the conflict warning
- **Stats**: "Warnings" counter should be > 0

---

### Test 5: Detect Unreachable Rules
Test detection of rules after DROP ALL.

**In Firewall Terminal:**
```bash
iptables -F INPUT
iptables -A INPUT -j DROP
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
```
- **Expected Logs**: 
  - WARNING: "Unreachable rules detected after DROP/REJECT all: Rule 2"
- **Explanation**: The second rule (accept port 80) will never be reached because the first rule drops everything

---

### Test 6: Test Multiple Chains
Test INPUT vs OUTPUT chain behavior.

**In Firewall Terminal:**
```bash
iptables -F INPUT
iptables -F OUTPUT
iptables -A OUTPUT -j DROP
```

**In LAN1 Terminal (Insider):**
```bash
nmap 10.0.0.50
```
- **Expected Logs**: "DROP" entries in OUTPUT chain (outgoing traffic blocked)

---

### Test 7: Complex Firewall Rules
Test realistic firewall configuration.

**In Firewall Terminal:**
```bash
iptables -F INPUT
iptables -F OUTPUT
iptables -F FORWARD

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED -j ACCEPT

# Allow SSH from internal network only
iptables -A INPUT -s 192.168.10.0/24 -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS to DMZ
iptables -A FORWARD -d 172.16.0.100 -p tcp --dport 80 -j ACCEPT
iptables -A FORWARD -d 172.16.0.100 -p tcp --dport 443 -j ACCEPT

# Drop everything else
iptables -A INPUT -j DROP
iptables -A FORWARD -j DROP
```

**Test from LAN2 (Outsider):**
```bash
nmap 192.168.10.10
```
- **Expected**: All ports blocked (external traffic)

**Test from LAN1 (Insider):**
```bash
nmap 192.168.10.10
```
- **Expected**: Port 22 allowed (internal SSH), others blocked

---

## Log Features Testing

### Filter Testing
1. Generate mixed traffic (some accepted, some dropped)
2. Click filter buttons to test:
   - **All**: Shows all log entries
   - **Blocked**: Shows only DROP/REJECT
   - **Allowed**: Shows only ACCEPT
   - **Warnings**: Shows only misconfiguration warnings

### Statistics Testing
- **Total Logs**: Should equal all log entries
- **Blocked**: Count of DROP/REJECT actions
- **Allowed**: Count of ACCEPT actions  
- **Warnings**: Count of misconfiguration detections

### Download Features

**Download Rules:**
- In Firewall Terminal: Click "Download Rules" button
- **Expected**: `.rules` file with all current iptables rules

**Download Logs:**
- Click "Download Logs" button in logs panel
- **Expected**: `.txt` file with:
  - Statistics summary
  - All log entries with timestamps
  - Detected warnings section

---

## Misconfiguration Detection Features

The simulator automatically detects:

1. **Conflicting Rules**: Same conditions, different targets
   ```bash
   iptables -A INPUT -p tcp --dport 80 -j ACCEPT
   iptables -A INPUT -p tcp --dport 80 -j DROP
   ```

2. **Unreachable Rules**: Rules after DROP/REJECT ALL
   ```bash
   iptables -A INPUT -j DROP
   iptables -A INPUT -p tcp --dport 22 -j ACCEPT  # Unreachable!
   ```

3. **Invalid Port Numbers**: Ports < 1 or > 65535

4. **Same Source/Destination**: Traffic with identical src/dst IPs

---

## Expected Behavior Summary

### Logs Panel Should Show:
- ✅ Real-time log updates as traffic is processed
- ✅ Color-coded entries:
  - 🔴 Red border = Blocked (DROP/REJECT)
  - 🟢 Green border = Allowed (ACCEPT)
  - 🟠 Orange border = Warnings
- ✅ Timestamps for each entry
- ✅ Rule information that triggered the action
- ✅ Warning messages for misconfigurations

### Statistics Should Display:
- ✅ Total number of log entries
- ✅ Number of blocked packets
- ✅ Number of allowed packets
- ✅ Number of warnings detected

### Filters Should Work:
- ✅ Clicking filter buttons updates displayed logs
- ✅ Active filter button is highlighted
- ✅ Real-time logs respect current filter

---

## Troubleshooting

**Issue**: Logs not appearing
- **Solution**: Check browser console for errors, refresh page

**Issue**: Filters not working
- **Solution**: Ensure filter buttons have click handlers, check JavaScript console

**Issue**: Stats not updating
- **Solution**: Verify `/api/logs` endpoint returns stats object

**Issue**: Download not working
- **Solution**: Check browser's download settings and popup blockers

---

## Educational Use Cases

### For Students:
1. **Learn Firewall Chains**: Understand INPUT vs OUTPUT vs FORWARD
2. **Rule Order Matters**: See how rule order affects traffic
3. **Security Best Practices**: Detect and fix misconfigurations
4. **Troubleshooting**: Use logs to debug blocked traffic
5. **Network Security**: Understand defense-in-depth concepts

### For Instructors:
1. **Lab Exercises**: Assign specific firewall configurations
2. **Assessment**: Review downloaded logs and rules
3. **Common Mistakes**: Show examples of misconfigurations
4. **Real-world Scenarios**: Simulate actual network attacks

---

## Advanced Testing

### Simulate Port Scan Attack
```bash
# In LAN2 (Attacker):
nmap 192.168.10.10
nmap 172.16.0.100
```
- Review logs for blocked connection attempts
- Download logs to analyze attack patterns

### DMZ Configuration
```bash
# In Firewall Terminal:
iptables -F FORWARD
iptables -A FORWARD -d 172.16.0.100 -p tcp --dport 80 -j ACCEPT
iptables -A FORWARD -d 172.16.0.100 -p tcp --dport 443 -j ACCEPT
iptables -A FORWARD -j DROP
```
- Test access to DMZ web server from different networks

---

## Credits
WebApp Firewall Simulator
Created by Van Glenndon Enad

For educational purposes - Network Security and Firewall Configuration Training
