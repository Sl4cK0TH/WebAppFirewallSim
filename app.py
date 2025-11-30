import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify, session
from flask_socketio import SocketIO, emit
import time
import random
import re
from datetime import datetime, timedelta
import ipaddress
import html
import os
import copy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'firewall-simulator-secret-key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=45)
socketio = SocketIO(app, cors_allowed_origins="*")

MAX_LOGS = 1000

def get_default_state():
    """Returns a deep copy of the default simulation state."""
    return copy.deepcopy({
        'network_config': {
            'insider': { 'ip': None, 'netmask': '255.255.255.0', 'gateway': None, 'network': None, 'zone': 'LAN1-INTERNAL' },
            'outsider': { 'ip': None, 'netmask': '255.255.255.0', 'gateway': None, 'network': None, 'zone': 'LAN2-EXTERNAL' },
            'dmz': { 'ip': None, 'netmask': '255.255.255.0', 'gateway': None, 'network': None, 'zone': 'DMZ-WEBSERVER' },
            'firewall': { 'ip': 'FIREWALL', 'netmask': '255.255.255.0', 'gateway': None, 'network': None, 'zone': 'FIREWALL-ADMIN' }
        },
        'iptables_rules': { 'INPUT': [], 'OUTPUT': [], 'FORWARD': [] },
        'rule_counters': { 'INPUT': [], 'OUTPUT': [], 'FORWARD': [] },
        'firewall_logs': []
    })

def log_firewall_event(action, source, destination, protocol, port, rule_info="", category="normal"):
    """Log firewall events with enhanced details to the current session."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sanitize all inputs to prevent XSS
    source = html.escape(str(source))
    destination = html.escape(str(destination))
    protocol = html.escape(str(protocol))
    port = html.escape(str(port)) if port is not None else None
    rule_info = html.escape(rule_info)
    
    # Detect potential misconfigurations
    warning = None
    if action in ['DROP', 'REJECT'] and category == "normal":
        # Check for potential misconfigurations
        if source == destination:
            warning = "MISCONFIGURATION: Source and destination are the same"
            category = "warning"
        elif port and int(port) > 65535:
            warning = "MISCONFIGURATION: Invalid port number"
            category = "warning"
    
    log_entry = {
        'timestamp': timestamp,
        'action': action,
        'source': source,
        'destination': destination,
        'protocol': protocol,
        'port': port,
        'rule': rule_info,
        'category': category,
        'warning': html.escape(warning) if warning else None,
        'details': f"{action} traffic from {source} to {destination} ({protocol}" + (f":{port}" if port else "") + ")"
    }
    session['firewall_logs'].append(log_entry)
    
    # Keep only last MAX_LOGS entries
    if len(session['firewall_logs']) > MAX_LOGS:
        session['firewall_logs'] = session['firewall_logs'][-MAX_LOGS:]
    
    # Broadcast log to the current client
    socketio.emit('new_log', log_entry)

def detect_rule_conflicts():
    """Detect potential rule conflicts and misconfigurations from the session."""
    warnings = []
    
    for chain in ['INPUT', 'OUTPUT', 'FORWARD']:
        rules = session['iptables_rules'][chain]
        
        # Check for conflicting rules
        for i, rule1 in enumerate(rules):
            for j, rule2 in enumerate(rules[i+1:], i+1):
                # Check if rules overlap but have different targets
                if (rule1['source'] == rule2['source'] and 
                    rule1['destination'] == rule2['destination'] and
                    rule1['protocol'] == rule2['protocol'] and
                    rule1['dport'] == rule2['dport'] and
                    rule1['target'] != rule2['target']):
                    warnings.append({
                        'type': 'CONFLICT',
                        'chain': chain,
                        'rules': [i+1, j+1],
                        'message': f"Rules {i+1} and {j+1} in {chain} chain conflict"
                    })
        
        # Check for unreachable rules (rules after DROP/REJECT ALL)
        for i, rule in enumerate(rules):
            if (rule['target'] in ['DROP', 'REJECT'] and 
                rule['source'] == '0.0.0.0/0' and 
                rule['destination'] == '0.0.0.0/0' and
                i < len(rules) - 1):
                warnings.append({
                    'type': 'UNREACHABLE',
                    'chain': chain,
                    'rule': i+1,
                    'message': f"Rules after rule {i+1} in {chain} are unreachable (DROP/REJECT ALL)"
                })
                break
    
    return warnings

def ip_in_network(ip, network):
    """Check if IP is in network range"""
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(network, strict=False)
    except:
        return False

def check_iptables_rule(chain, source_ip, dest_ip, protocol, port):
    """Check if traffic matches iptables rules in the current session."""
    rules = session['iptables_rules'].get(chain, [])
    
    for idx, rule in enumerate(rules):
        # Check source
        if rule['source'] and rule['source'] != '0.0.0.0/0':
            if '/' in rule['source']:
                if not ip_in_network(source_ip, rule['source']):
                    continue
            elif source_ip != rule['source']:
                continue
        
        # Check destination
        if rule['destination'] and rule['destination'] != '0.0.0.0/0':
            if '/' in rule['destination']:
                if not ip_in_network(dest_ip, rule['destination']):
                    continue
            elif dest_ip != rule['destination']:
                continue
        
        # Check protocol
        if rule['protocol'] and rule['protocol'] != 'all':
            if protocol.lower() != rule['protocol'].lower():
                continue
        
        # Check port
        if rule['dport'] and port:
            if str(port) != str(rule['dport']):
                continue
        
        # Rule matched - increment counter
        if idx < len(session['rule_counters'][chain]):
            session['rule_counters'][chain][idx]['packets'] += 1
            session['rule_counters'][chain][idx]['bytes'] += random.randint(40, 1500)
        
        # Log if LOG action
        if rule['target'] == 'LOG':
            log_firewall_event('LOG', source_ip, dest_ip, protocol, port, f"{chain} rule {idx+1}")
            continue  # LOG doesn't stop processing
        
        # Return action
        if rule['target'] == 'ACCEPT':
            log_firewall_event('ACCEPT', source_ip, dest_ip, protocol, port, f"{chain} rule {idx+1}")
            return True, f"ACCEPT by {chain} rule {idx+1}"
        elif rule['target'] == 'DROP':
            log_firewall_event('DROP', source_ip, dest_ip, protocol, port, f"{chain} rule {idx+1}")
            return False, f"DROP by {chain} rule {idx+1}"
        elif rule['target'] == 'REJECT':
            log_firewall_event('REJECT', source_ip, dest_ip, protocol, port, f"{chain} rule {idx+1}")
            return False, f"REJECT by {chain} rule {idx+1}"
    
    # Default policy - DROP
    log_firewall_event('DROP', source_ip, dest_ip, protocol, port, "Default policy")
    return False, "DROP by default policy"

def calculate_network(ip_address):
    """Calculate network address from IP"""
    try:
        ip = ipaddress.ip_address(ip_address)
        # Create network with /24 mask
        network = ipaddress.ip_network(f"{ip_address}/24", strict=False)
        gateway = str(network.network_address + 1)  # .1 is typically gateway
        return str(network), gateway
    except:
        return None, None

def handle_ifconfig_command(terminal, parts):
    """Handle ifconfig commands within the current session."""
    if len(parts) == 1:
        # Show current configuration
        config = session['network_config'][terminal]
        if config['ip']:
            output = f"eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\n"
            output += f"        inet {config['ip']}  netmask {config['netmask']}  broadcast {config['gateway']}\n"
            output += f"        ether 02:42:ac:11:00:{random.randint(10,99)}  txqueuelen 0  (Ethernet)\n"
            output += f"        RX packets 1234  bytes 567890 (567.8 KB)\n"
            output += f"        TX packets 987  bytes 123456 (123.4 KB)\n\n"
            output += f"Zone: {config['zone']}\n"
            output += f"Network: {config['network']}\n"
            return output
        else:
            return f"eth0: No IP address configured\nUse: ifconfig set ip <ip_address>\n"
    
    elif len(parts) >= 4 and parts[1] == 'set' and parts[2] == 'ip':
        # Set IP address
        ip = parts[3]
        try:
            # Validate IP
            ipaddress.ip_address(ip)
            
            # Calculate network and gateway
            network, gateway = calculate_network(ip)
            
            # Update configuration in session
            session['network_config'][terminal]['ip'] = ip
            session['network_config'][terminal]['network'] = network
            session['network_config'][terminal]['gateway'] = gateway
            
            # Update display
            socketio.emit('update_ip_display', {
                'terminal': terminal,
                'ip': html.escape(ip),
                'network': html.escape(network) if network else None
            })
            return f"IP address set to {html.escape(ip)}\nNetwork: {html.escape(network)}\nGateway: {html.escape(gateway)}\n"
        except:
            return f"Invalid IP address: {html.escape(ip)}\n"
    
    else:
        return "Usage: ifconfig [set ip <ip_address>]\n"

def handle_iptables_command(terminal, parts):
    """Handle iptables commands within the current session."""
    if len(parts) < 2:
        return "Usage: iptables [-A|-D|-L|-F] [chain] [options]\n"
    
    option = parts[1]
    
    # List rules
    if option == '-L':
        output = "\n"
        verbose = '-v' in parts
        
        for chain in ['INPUT', 'OUTPUT', 'FORWARD']:
            output += f"Chain {chain} (policy DROP)\n"
            if verbose:
                output += f"{'pkts':<8} {'bytes':<10} {'target':<12} {'prot':<6} {'source':<20} {'destination':<20} {'options'}\n"
            else:
                output += f"{'target':<12} {'prot':<6} {'source':<20} {'destination':<20}\n"
            
            for idx, rule in enumerate(session['iptables_rules'][chain]):
                if verbose and idx < len(session['rule_counters'][chain]):
                    pkts = session['rule_counters'][chain][idx]['packets']
                    bytes_count = session['rule_counters'][chain][idx]['bytes']
                    output += f"{pkts:<8} {bytes_count:<10} "
                
                # Sanitize rule components for display
                target = html.escape(rule['target'])
                protocol = html.escape(rule['protocol'])
                source = html.escape(rule['source'])
                destination = html.escape(rule['destination'])
                
                output += f"{target:<12} {protocol:<6} {source:<20} {destination:<20}"
                
                if rule['dport']:
                    output += f" dpt:{html.escape(rule['dport'])}"
                if rule['sport']:
                    output += f" spt:{html.escape(rule['sport'])}"
                
                output += "\n"
            output += "\n"
        
        return output
    
    # Flush rules
    elif option == '-F':
        chain = parts[2] if len(parts) > 2 else None
        if chain:
            if chain in session['iptables_rules']:
                session['iptables_rules'][chain] = []
                session['rule_counters'][chain] = []
                return f"Flushed {chain} chain\n"
            else:
                return f"Invalid chain: {chain}\n"
        else:
            for chain in session['iptables_rules']:
                session['iptables_rules'][chain] = []
                session['rule_counters'][chain] = []
            return "Flushed all chains\n"
    
    # Append rule
    elif option == '-A':
        if len(parts) < 3:
            return "Usage: iptables -A <chain> [options]\n"
        
        chain = parts[2]
        if chain not in session['iptables_rules']:
            return f"Invalid chain: {chain}. Use INPUT, OUTPUT, or FORWARD\n"
        
        # Parse rule options
        rule = {
            'source': '0.0.0.0/0', 'destination': '0.0.0.0/0', 'protocol': 'all',
            'sport': None, 'dport': None, 'target': 'DROP'
        }
        
        i = 3
        while i < len(parts):
            if parts[i] == '-s' and i + 1 < len(parts): rule['source'] = parts[i + 1]; i += 2
            elif parts[i] == '-d' and i + 1 < len(parts): rule['destination'] = parts[i + 1]; i += 2
            elif parts[i] == '-p' and i + 1 < len(parts): rule['protocol'] = parts[i + 1]; i += 2
            elif parts[i] == '--sport' and i + 1 < len(parts): rule['sport'] = parts[i + 1]; i += 2
            elif parts[i] == '--dport' and i + 1 < len(parts): rule['dport'] = parts[i + 1]; i += 2
            elif parts[i] == '-j' and i + 1 < len(parts): rule['target'] = parts[i + 1]; i += 2
            else: i += 1
        
        # Prevent duplicate rules
        if rule in session['iptables_rules'][chain]:
            return "iptables: Rule already exists.\n"

        session['iptables_rules'][chain].append(rule)
        session['rule_counters'][chain].append({'packets': 0, 'bytes': 0})
        
        return f"Rule added to {chain} chain\n"
    
    # Delete rule
    elif option == '-D':
        if len(parts) < 4:
            return "Usage: iptables -D <chain> <rule_number>\n"
        
        chain = parts[2]
        try:
            rule_num = int(parts[3]) - 1
            if chain in session['iptables_rules'] and 0 <= rule_num < len(session['iptables_rules'][chain]):
                del session['iptables_rules'][chain][rule_num]
                del session['rule_counters'][chain][rule_num]
                return f"Deleted rule {rule_num + 1} from {chain} chain\n"
            else:
                return f"Invalid rule number\n"
        except ValueError:
            return "Rule number must be an integer\n"
    
    else:
        return f"Unknown option: {option}\n"

def handle_nmap_command(terminal, parts):
    """Handle nmap port scanning within the current session."""
    if len(parts) < 2:
        return "Usage: nmap [-p <ports>] <target>\n"
    
    ports_to_scan = [80, 443, 22, 21, 23, 25, 53, 3306]
    target = None
    
    i = 1
    while i < len(parts):
        if parts[i] == '-p' and i + 1 < len(parts):
            port_spec = parts[i + 1]; i += 2
            if ',' in port_spec: ports_to_scan = [int(p) for p in port_spec.split(',')]
            elif '-' in port_spec: start, end = map(int, port_spec.split('-')); ports_to_scan = list(range(start, end + 1))
            else: ports_to_scan = [int(port_spec)]
        else: target = parts[i]; i += 1
    
    if not target:
        return "Error: No target specified\n"
    
    source_ip = session['network_config'][terminal]['ip']
    if not source_ip:
        return "Error: No IP address configured. Use 'ifconfig set ip <ip>'\n"
    
    safe_target = html.escape(target)
    output = f"\nStarting Nmap scan on {safe_target}\n"
    output += f"Nmap scan report for {safe_target}\n"
    output += f"Host is up (0.0010s latency).\n\n"
    output += f"{'PORT':<10} {'STATE':<12} {'SERVICE'}\n"
    
    for port in ports_to_scan:
        allowed, message = check_iptables_rule('FORWARD', source_ip, target, 'tcp', port)
        
        if allowed:
            state = random.choice(['open', 'open', 'open', 'closed'])
            service = { 80: 'http', 443: 'https', 22: 'ssh', 21: 'ftp', 23: 'telnet', 25: 'smtp', 53: 'dns', 3306: 'mysql' }.get(port, 'unknown')
            output += f"{port}/tcp{'':<3} {state:<12} {service}\n"
        else:
            output += f"{port}/tcp{'':<3} {'filtered':<12} (blocked by firewall)\n"
        
        time.sleep(0.05)
    
    output += f"\nNmap done: 1 IP address scanned\n"
    return output

def handle_ping_command(terminal, target):
    """Handle ping command with firewall checking within the current session."""
    source_ip = session['network_config'][terminal]['ip']
    if not source_ip:
        return "Error: No IP address configured. Use 'ifconfig set ip <ip>'\n"
    
    safe_target = html.escape(target)
    allowed, message = check_iptables_rule('FORWARD', source_ip, target, 'icmp', None)
    
    if not allowed:
        return f"ping: {safe_target}: {html.escape(message)}\n"
    
    output = f"PING {safe_target} 56(84) bytes of data.\n"
    for i in range(4):
        ttl = random.randint(50, 64)
        latency = random.uniform(0.5, 50.0)
        output += f"64 bytes from {safe_target}: icmp_seq={i+1} ttl={ttl} time={latency:.1f} ms\n"
        time.sleep(0.1)
    
    output += f"\n--- {safe_target} ping statistics ---\n"
    output += f"4 packets transmitted, 4 received, 0% packet loss\n"
    return output

def init_session_if_needed():
    """Initializes the simulation state if not already in the session."""
    if 'initialized' not in session:
        session.permanent = True
        session.update(get_default_state())
        session['initialized'] = True
        lifetime = app.config['PERMANENT_SESSION_LIFETIME'].total_seconds()
        socketio.emit('session_initialized', {'lifetime': lifetime})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rules')
def get_rules():
    """API endpoint to get session-specific rules for download"""
    init_session_if_needed()
    print(f"DEBUG: Session in /api/rules: {session}")
    rules_text = "# Firewall Rules Configuration\n"
    rules_text += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for chain in ['INPUT', 'OUTPUT', 'FORWARD']:
        rules_text += f"# {chain} Chain\n"
        for rule in session['iptables_rules'][chain]:
            cmd = f"iptables -A {chain}"
            if rule['source'] != '0.0.0.0/0': cmd += f" -s {rule['source']}"
            if rule['destination'] != '0.0.0.0/0': cmd += f" -d {rule['destination']}"
            if rule['protocol'] != 'all': cmd += f" -p {rule['protocol']}"
            if rule['sport']: cmd += f" --sport {rule['sport']}"
            if rule['dport']: cmd += f" --dport {rule['dport']}"
            cmd += f" -j {rule['target']}"
            rules_text += cmd + "\n"
        rules_text += "\n"
    
    return jsonify({'rules': rules_text})

@app.route('/api/logs')
def get_logs():
    """API endpoint to get session-specific firewall logs"""
    init_session_if_needed()
    warnings = detect_rule_conflicts()
    
    return jsonify({
        'logs': session['firewall_logs'],
        'warnings': warnings,
        'stats': {
            'total': len(session['firewall_logs']),
            'blocked': len([l for l in session['firewall_logs'] if l['action'] in ['DROP', 'REJECT']]),
            'allowed': len([l for l in session['firewall_logs'] if l['action'] == 'ACCEPT']),
            'warnings': len([l for l in session['firewall_logs'] if l['category'] == 'warning']) + len(warnings)
        }
    })

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs_endpoint():
    """API endpoint to clear session-specific logs and counters"""
    init_session_if_needed()
    session['firewall_logs'] = []
    
    # Reset rule counters
    for chain in session['rule_counters']:
        for counter in session['rule_counters'][chain]:
            counter['packets'] = 0
            counter['bytes'] = 0
            
    log_firewall_event('INFO', 'N/A', 'N/A', 'N/A', None, "Logs and statistics cleared", 'info')
    
    return jsonify({'status': 'success', 'message': 'Logs and counters cleared'})

@socketio.on('connect')
def handle_connect():
    """Handle new client connection and initialize their session."""
    init_session_if_needed()
    print('Client connected')
    emit('connected', {'data': 'Connected to firewall simulator'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('command')
def handle_command(data):
    """Handle terminal commands from clients for the current session."""
    init_session_if_needed()
    terminal = data.get('terminal', 'insider')
    command = data.get('command', '').strip()
    
    if not command:
        return
    
    parts = command.split()
    cmd = parts[0].lower()
    
    output = ""
    
    try:
        if cmd == 'help':
            output = """
Available commands:

Network Configuration:
  ifconfig                    - Show network configuration
  ifconfig set ip <ip>        - Set IP address for this terminal

Firewall Management:
  iptables -L [-v]            - List all firewall rules (-v for verbose)
  iptables -A <chain> [opts]  - Append rule to chain
    Options: -s <source> -d <dest> -p <protocol> --dport <port> -j <target>
    Chains: INPUT, OUTPUT, FORWARD
    Targets: ACCEPT, DROP, REJECT, LOG
  iptables -D <chain> <num>   - Delete rule number from chain
  iptables -F [chain]         - Flush all rules (or specific chain)

Network Testing:
  ping <target>               - Test ICMP connectivity
  nmap [-p <ports>] <target>  - Scan ports (use -p 80,443 or -p 1-1000)
  nc <target> <port>          - Test TCP connection
  curl <url>                  - HTTP request

Network Utilities:
  traceroute <target>         - Trace route to target
  nslookup <domain>           - DNS lookup
  whoami                      - Show terminal info
  clear                       - Clear terminal

Examples:
  ifconfig set ip 192.168.10.10
  iptables -A FORWARD -s 192.168.10.0/24 -p tcp --dport 80 -j ACCEPT
  iptables -A FORWARD -d 192.168.10.0/24 -j DROP
  nmap -p 80,443 192.168.30.10
  iptables -L -v
"""
        
        elif cmd == 'ifconfig':
            output = handle_ifconfig_command(terminal, parts)
        
        elif cmd == 'iptables':
            output = handle_iptables_command(terminal, parts)
        
        elif cmd == 'nmap':
            output = handle_nmap_command(terminal, parts)
        
        elif cmd == 'ping':
            if len(parts) < 2:
                output = "Usage: ping <target>\n"
            else:
                output = handle_ping_command(terminal, parts[1])
        
        elif cmd == 'whoami':
            config = session['network_config'][terminal]
            output = f"Terminal: {terminal}\n"
            output += f"Zone: {config['zone']}\n"
            output += f"Network: {config['network']}\n"
            output += f"IP: {config['ip'] or 'Not configured'}\n"
        
        elif cmd == 'clear':
            emit('clear', {'terminal': terminal})
            return
        
        elif cmd == 'traceroute':
            if len(parts) < 2:
                output = "Usage: traceroute <target>\n"
            else:
                target = parts[1]
                safe_target = html.escape(target)
                output = f"traceroute to {safe_target}, 30 hops max, 60 byte packets\n"
                for i in range(1, random.randint(5, 12) + 1):
                    ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                    latency = random.uniform(1.0, 50.0) * i
                    output += f" {i}  {ip}  {latency:.3f} ms\n"
                    time.sleep(0.05)
        
        elif cmd == 'nslookup':
            if len(parts) < 2:
                output = "Usage: nslookup <domain>\n"
            else:
                domain = parts[1]
                safe_domain = html.escape(domain)
                ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                output = f"Server:  8.8.8.8\nAddress: 8.8.8.8#53\n\n"
                output += f"Name: {safe_domain}\nAddress: {ip}\n"
        
        elif cmd == 'nc':
            if len(parts) < 3:
                output = "Usage: nc <target> <port>\n"
            else:
                source_ip = session['network_config'][terminal]['ip']
                if not source_ip:
                    output = "Error: No IP address configured\n"
                else:
                    target, port = parts[1], parts[2]
                    safe_target = html.escape(target)
                    safe_port = html.escape(port)
                    allowed, message = check_iptables_rule('FORWARD', source_ip, target, 'tcp', port)
                    if allowed:
                        output = f"Connection to {safe_target} {safe_port} port [tcp/*] succeeded!\n"
                    else:
                        output = f"nc: connect to {safe_target} port {safe_port} (tcp) failed: {html.escape(message)}\n"
        
        elif cmd == 'curl':
            if len(parts) < 2:
                output = "Usage: curl <url>\n"
            else:
                source_ip = session['network_config'][terminal]['ip']
                if not source_ip:
                    output = "Error: No IP address configured\n"
                else:
                    url = parts[1]
                    safe_url = html.escape(url)
                    # Extract target IP from URL (simplified)
                    if '192.168.' in url:
                        target = url.split('/')[2] if '/' in url else url
                    else:
                        target = '8.8.8.8'
                    
                    port = '443' if 'https' in url else '80'
                    allowed, message = check_iptables_rule('FORWARD', source_ip, target, 'tcp', port)
                    if allowed:
                        output = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><body>Response from {safe_url}</body></html>\n"
                    else:
                        output = f"curl: (7) Failed to connect: {html.escape(message)}\n"
        
        else:
            output = f"bash: {cmd}: command not found\nType 'help' for available commands\n"
    
    except Exception as e:
        output = f"Error: {str(e)}\n"
    
    emit('output', {
        'terminal': terminal,
        'output': output
    })

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    print("="*60)
    print("WebApp Firewall Simulator - Educational Tool")
    print(f"  Mode: {'Development' if debug_mode else 'Production'}")
    print("="*60)
    print(f"Server starting at: http://localhost:{port}")
    print("\nExample commands:")
    print("  ifconfig set ip 192.168.10.10")
    print("  iptables -A OUTPUT -p tcp --dport 80 -j ACCEPT")
    print("  nmap -p 80,443 192.168.30.10")
    print("="*60)
    
    socketio.run(
        app,
        debug=debug_mode,
        host='0.0.0.0',
        port=port,
        allow_unsafe_werkzeug=True
    )
