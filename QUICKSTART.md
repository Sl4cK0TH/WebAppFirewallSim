# Quick Start Guide

## 🚀 Get Started in 30 Seconds

### Using Docker (Easiest)

```bash
# Clone the repository
git clone <repository-url> WebAppFirewallSimulator
cd WebAppFirewallSimulator

# Run with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:5000
```

### Using Python

```bash
# Clone the repository
git clone <repository-url> WebAppFirewallSimulator
cd WebAppFirewallSimulator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access the application
open http://localhost:5000
```

## ⚡ First Steps in the Simulator

1. **Configure Network IPs** (in each terminal):
   ```bash
   # LAN1 Terminal
   ifconfig set ip 192.168.10.10
   
   # LAN2 Terminal  
   ifconfig set ip 10.0.0.50
   
   # DMZ Terminal
   ifconfig set ip 172.16.0.100
   ```

2. **Configure Firewall** (in Firewall terminal):
   ```bash
   # Allow SSH from internal network
   iptables -A INPUT -s 192.168.10.0/24 -p tcp --dport 22 -j ACCEPT
   
   # Allow HTTP/HTTPS to DMZ
   iptables -A FORWARD -d 172.16.0.100 -p tcp --dport 80 -j ACCEPT
   iptables -A FORWARD -d 172.16.0.100 -p tcp --dport 443 -j ACCEPT
   
   # Drop everything else
   iptables -A INPUT -j DROP
   iptables -A FORWARD -j DROP
   ```

3. **Test Connectivity** (in LAN2 terminal):
   ```bash
   nmap 172.16.0.100
   ```

4. **View Logs**:
   - Click filter buttons: All, Blocked, Allowed, Warnings
   - Download logs for analysis

## 📚 Learn More

- **Full Documentation**: [README.md](README.md)
- **Docker Guide**: [DOCKER.md](DOCKER.md)
- **Testing Scenarios**: [TESTING_GUIDE.md](TESTING_GUIDE.md)

## 🎯 Common Use Cases

### Block All External Traffic
```bash
iptables -A INPUT -s 10.0.0.0/8 -j DROP
```

### Allow Web Traffic
```bash
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### View Current Rules
```bash
iptables -L -v
```

### Download Configuration
- Click "Download Rules" in Firewall terminal
- Click "Download Logs" in Logs panel

---

Created by **Van Glenndon Enad**
