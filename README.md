# 🔥 WebApp Firewall Simulator

An educational web-based firewall simulator for learning network security and Linux iptables configuration. Built for students and instructors to understand firewall behavior, rule configuration, and network security concepts in a safe, simulated environment.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-Educational-yellow)

Created by **Van Glenndon Enad**

---

## 🎯 Features

### ✨ Four Interactive Terminals
- **LAN1 (Internal Network)**: Simulates internal corporate network
- **LAN2 (External Network)**: Simulates external/internet traffic
- **DMZ (Web Server)**: Simulates demilitarized zone hosting public services
- **Firewall (Admin)**: Dedicated terminal for firewall configuration

### 🛠️ Command Reference
The simulator provides a variety of realistic Linux commands for network configuration, testing, and firewall management.

| Command | Description | Example |
| :--- | :--- | :--- |
| `help` | Displays a list of all available commands. | `help` |
| `ifconfig` | Displays the IP address of a terminal. | `ifconfig` |
| `ifconfig set ip <ip>` | Configures the IP address for a terminal. | `ifconfig set ip 192.168.10.10` |
| `ping <target>` | Sends ICMP packets to test network connectivity. | `ping 10.0.0.50` |
| `nmap <target>` | Scans a target for open ports. | `nmap -p 80,443 172.16.0.100` |
| `curl <url>` | Simulates an HTTP request to a URL. | `curl http://172.16.0.100` |
| `nc <host> <port>` | Tests TCP connectivity to a specific host and port. | `nc 172.16.0.100 80` |
| `traceroute <target>` | Traces the network path to a target host. | `traceroute 8.8.8.8` |
| `nslookup <domain>` | Performs a simulated DNS lookup. | `nslookup google.com` |
| `whoami` | Displays the current terminal's zone and IP info. | `whoami` |
| `clear` | Clears the terminal screen. | `clear` |

#### Firewall Management (`iptables`)
The `iptables` command is used to configure the firewall from the **Firewall (Admin)** terminal.

| Command | Description |
| :--- | :--- |
| `iptables -L [-v]` | Lists all rules in all chains. `-v` shows packet/byte counters. |
| `iptables -F [chain]` | Flushes (deletes) all rules. Can specify a chain (`INPUT`, `OUTPUT`, `FORWARD`). |
| `iptables -A <chain> [opts]`| Appends a new rule to a chain. |
| `iptables -D <chain> <num>` | Deletes a rule by its number in the chain. |

**Rule Options (`[opts]`):**
- `-s <ip/net>`: Specifies the **source** address (e.g., `192.168.10.0/24`).
- `-d <ip/net>`: Specifies the **destination** address.
- `-p <protocol>`: Specifies the protocol (`tcp`, `udp`, `icmp`).
- `--dport <port>`: Specifies the destination **port** (for `tcp` or `udp`).
- `-j <target>`: Specifies the **target** action to take.

**Targets (`<target>`):**
- `ACCEPT`: Allows the packet.
- `DROP`: Silently drops the packet (automatically logged as **Blocked**).
- `REJECT`: Blocks the packet and notifies the sender (automatically logged as **Blocked**).
- `LOG`: Explicitly logs the packet and continues processing rules (useful for debugging).

### 📊 Comprehensive Logging System
- **Real-time Logs**: See firewall actions as they happen
- **Categorized Logs**:
  - 🟢 **Allowed**: ACCEPT actions
  - 🔴 **Blocked**: DROP/REJECT actions
  - 🟠 **Warnings**: Misconfigurations detected
- **Smart Filters**: Filter logs by category (All, Blocked, Allowed, Warnings)
- **Statistics Dashboard**: Track total, blocked, allowed, and warning counts
- **Download Logs**: Export logs with timestamps and statistics

### 🔍 Misconfiguration Detection
- **Conflicting Rules**: Detects rules with same conditions but different targets
- **Unreachable Rules**: Warns about rules after DROP/REJECT ALL
- **Invalid Configurations**: Identifies invalid port numbers and network settings
- **Traffic Anomalies**: Flags suspicious traffic patterns

### 🌐 Dynamic Network Topology
- Automatic subnet calculation (e.g., 192.168.10.10 → 192.168.10.0/24)
- Real-time IP address display
- Network range visualization
- Proper network segmentation (LAN1, LAN2, DMZ)

### 💾 Export Features
- **Download Rules**: Export current iptables configuration
- **Download Logs**: Export comprehensive logs with statistics and warnings

---

## 🚀 Installation

### Option 1: Docker (Recommended)

The easiest way to run the simulator is using Docker:

```bash
# Using the deployment script
./docker-deploy.sh

# Or manually with Docker Compose
docker-compose up -d

# Or with Docker CLI
docker build -t webapp-firewall-simulator .
docker run -d -p 5000:5000 webapp-firewall-simulator
```

**Access:** http://localhost:5000

📖 See [DOCKER.md](DOCKER.md) for complete Docker deployment guide.

### Option 2: Local Installation (From Source)

For developers who want to run the application from the source code or contribute to the project, here is how to set it up on your local machine.

#### Prerequisites
- **Python**: Version 3.12 or higher. On some systems, you may need to use the `python3` command instead of `python`.
- **pip**: The Python package manager, which typically comes with your Python installation.
- **Git**: For cloning the project repository.
- **Web Browser**: A modern browser like Chrome, Firefox, or Edge.

#### Setup Steps

1. **Clone the Repository**
   First, clone the project repository from GitHub to your local machine.
   ```bash
   # TODO: Replace with your actual repository URL after creating it on GitHub
   git clone https://github.com/your-username/WebAppFirewallSimulator.git
   cd WebAppFirewallSimulator
   ```

2. **Create a Virtual Environment**
   It is a best practice to use a virtual environment to isolate project dependencies and avoid conflicts with other Python projects.
   ```bash
   # Create the virtual environment in a folder named .venv
   python -m venv .venv

   # Activate the environment to use it
   source .venv/bin/activate  # On Linux/macOS
   # OR
   .venv\Scripts\activate      # On Windows
   ```
   When activated, you should see `(.venv)` at the beginning of your terminal prompt.

3. **Install Dependencies**
   Install all the required Python packages using pip and the `requirements.txt` file.
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   With the virtual environment active and dependencies installed, you can now run the simulator.
   ```bash
   python app.py
   ```
   You will see terminal output indicating that the server is running and accessible at `http://localhost:5000`.

5. **Access the Simulator**
   Open your web browser and navigate to the following URL:
   - **URL**: `http://localhost:5000`
   - The simulator is now ready to use!

---

## 📚 Usage Guide

### Basic Network Configuration

1. **Configure LAN1 (Internal)**
   ```bash
   ifconfig set ip 192.168.10.10
   ```

2. **Configure LAN2 (External)**
   ```bash
   ifconfig set ip 10.0.0.50
   ```

3. **Configure DMZ (Web Server)**
   ```bash
   ifconfig set ip 172.16.0.100
   ```

### Firewall Configuration Examples

#### Block All Incoming Traffic
```bash
# In Firewall Terminal:
iptables -A INPUT -j DROP
```

#### Allow Specific Port (SSH)
```bash
iptables -F INPUT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -j DROP
```

#### DMZ Configuration (Web Server)
```bash
# Allow HTTP/HTTPS to DMZ
iptables -A FORWARD -d 172.16.0.100 -p tcp --dport 80 -j ACCEPT
iptables -A FORWARD -d 172.16.0.100 -p tcp --dport 443 -j ACCEPT
iptables -A FORWARD -j DROP
```

#### Internal Network Protection
```bash
# Allow SSH from internal network only
iptables -A INPUT -s 192.168.10.0/24 -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j DROP
```

### Testing Firewall Rules

#### Port Scanning
```bash
# From LAN2 (External):
nmap 192.168.10.10
```

#### Connectivity Testing
```bash
# From LAN1:
ping 10.0.0.50
nc 172.16.0.100 80
curl http://172.16.0.100
```

### Viewing and Analyzing Logs

1. **Filter Logs**:
   - Click "All" to see all logs
   - Click "Blocked" to see only dropped traffic
   - Click "Allowed" to see only accepted traffic
   - Click "Warnings" to see misconfigurations

2. **View Statistics**:
   - Total logs count
   - Blocked traffic count
   - Allowed traffic count
   - Warnings count

3. **Export Logs**:
   - Click "Download Logs" to export all logs
   - Click "Download Rules" to export firewall configuration

---

## 🎓 Educational Use Cases

### For Students
- **Learn iptables**: Hands-on practice with Linux firewall commands
- **Understand Chains**: See how INPUT, OUTPUT, and FORWARD chains work
- **Rule Order**: Discover why rule order matters in firewalls
- **Troubleshooting**: Use logs to debug blocked traffic
- **Security Concepts**: Learn defense-in-depth, DMZ, network segmentation

### For Instructors
- **Lab Assignments**: Create firewall configuration exercises
- **Assessment**: Review student configurations via downloaded rules
- **Live Demos**: Demonstrate security concepts in real-time
- **Attack Simulation**: Show port scans and blocking techniques
- **Best Practices**: Teach secure firewall configuration

### Example Lab Exercises
1. **Basic Firewall**: Configure firewall to allow only SSH and HTTP
2. **DMZ Setup**: Create a DMZ zone with web server access
3. **Attack Defense**: Block port scans and log suspicious traffic
4. **Troubleshooting**: Fix intentionally misconfigured firewalls
5. **Network Segmentation**: Implement multi-zone security policies

---

## 🏗️ Architecture

### Backend (Flask + Socket.IO)
- **app.py**: Main Flask application
  - Network configuration management
  - iptables rule simulation
  - Command parsing and execution
  - Firewall logging system
  - Misconfiguration detection
  - RESTful API endpoints

### Frontend
- **index.html**: Main UI structure
  - Four terminal panels
  - Logs panel with filters
  - Network topology display
- **script.js**: Terminal management and real-time updates
  - xterm.js integration
  - Socket.IO client
  - Log filtering and statistics
  - Download functionality
- **styles.css**: Responsive UI styling
  - Terminal themes
  - Log entry styling
  - Network visualization

### Technologies
- **Backend**: Flask 3.0, Flask-SocketIO 5.3, Python 3.12
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Terminal**: xterm.js 5.3.0
- **Communication**: Socket.IO (WebSockets)
- **Network Simulation**: Python ipaddress module

---

## 📋 Requirements

```
Flask==3.0.0
Flask-SocketIO==5.3.6
python-socketio==5.10.0
```

---

## 🔧 Development

### Project Structure
```
WebAppFirewallSimulator/
├── app.py                 # Flask backend
├── templates/
│   └── index.html        # Main UI
├── static/
│   ├── script.js         # Frontend logic
│   └── styles.css        # Styling
├── .venv/                # Virtual environment
├── requirements.txt      # Dependencies
├── README.md            # This file
└── TESTING_GUIDE.md     # Comprehensive testing guide
```

### Running in Development Mode
```bash
source .venv/bin/activate
export FLASK_ENV=development
python app.py
```

### Testing
See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing scenarios.

---

## 🐛 Troubleshooting

### Server Won't Start
- **Check Python version**: `python --version` (requires 3.12+)
- **Activate virtual environment**: `source .venv/bin/activate`
- **Install dependencies**: `pip install -r requirements.txt`

### Terminals Not Appearing
- **Check browser console**: F12 → Console tab
- **Clear browser cache**: Ctrl+Shift+Delete
- **Try different browser**: Chrome, Firefox, Edge

### Commands Not Working
- **Check terminal focus**: Click inside terminal before typing
- **Verify syntax**: Use exact command syntax from examples
- **Check logs panel**: Look for error messages

### Logs Not Updating
- **Refresh page**: F5 or Ctrl+R
- **Check network**: Verify Socket.IO connection in console
- **Restart server**: `python app.py`

---

## 🎯 Features Roadmap

### Current Version (v1.0)
- ✅ Four interactive terminals
- ✅ Complete iptables simulation
- ✅ Comprehensive logging with filters
- ✅ Misconfiguration detection
- ✅ Download rules and logs
- ✅ Dynamic network topology
- ✅ Real-time updates via WebSockets

### Future Enhancements
- 🔜 Save/load firewall configurations
- 🔜 Pre-configured scenario templates
- 🔜 Multi-user support for classroom use
- 🔜 Packet capture visualization
- 🔜 Traffic graphing and analytics
- 🔜 Advanced protocol simulation (DNS, DHCP)
- 🔜 IDS/IPS integration simulation

---

## 📖 Learning Resources

### Recommended Reading
- Linux iptables documentation
- Network security fundamentals
- TCP/IP protocol basics
- Firewall design principles

### Related Topics
- Network segmentation
- DMZ architecture
- Port scanning techniques
- Intrusion detection systems
- Security policy design

---

## 🤝 Contributing

This is an educational project. Contributions, suggestions, and improvements are welcome!

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📝 License

This project is created for educational purposes.

---

## 👨‍💻 Author

**Van Glenndon Enad**

Created for educational purposes to help students learn network security and firewall configuration in a safe, interactive environment.

---

## 🙏 Acknowledgments

- Flask and Flask-SocketIO teams
- xterm.js project
- Socket.IO developers
- Network security community

---

## 📧 Support

For issues, questions, or suggestions:
1. Check the [TESTING_GUIDE.md](TESTING_GUIDE.md)
2. Review troubleshooting section
3. Open an issue in the repository

---

## 🌟 Star This Project

If you find this educational tool helpful, please give it a star! ⭐

---

**Happy Firewall Learning! 🔥🛡️**
