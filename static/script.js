// Initialize Socket.IO connection
const socket = io();

// Terminal instances
const terminals = {
    firewall: null,
    insider: null,
    outsider: null,
    dmz: null
};

// Command buffers for each terminal
const commandBuffers = {
    firewall: '',
    insider: '',
    outsider: '',
    dmz: ''
};

// Initialize xterm.js terminals
function initializeTerminals() {
    const terminalConfigs = [
        { id: 'firewall', element: 'terminal-firewall', title: 'FIREWALL ADMIN', color: '#764ba2' },
        { id: 'insider', element: 'terminal-insider', title: 'LAN1-INTERNAL', color: '#37b24d' },
        { id: 'outsider', element: 'terminal-outsider', title: 'LAN2-EXTERNAL', color: '#c92a2a' },
        { id: 'dmz', element: 'terminal-dmz', title: 'DMZ-WEBSERVER', color: '#f59f00' }
    ];

    terminalConfigs.forEach(config => {
        // Create terminal instance
        const term = new Terminal({
            cursorBlink: true,
            fontSize: 14,
            fontFamily: 'Courier New, monospace',
            theme: {
                background: '#000000',
                foreground: '#00ff00',
                cursor: '#00ff00',
                selection: 'rgba(255, 255, 255, 0.3)',
                black: '#000000',
                red: '#ff6b6b',
                green: '#6bcf7f',
                yellow: '#ffd93d',
                blue: '#4dabf7',
                magenta: '#cc5de8',
                cyan: '#22b8cf',
                white: '#ffffff'
            },
            rows: 20,
            cols: 80
        });

        // Create fit addon for responsive sizing
        const fitAddon = new FitAddon.FitAddon();
        term.loadAddon(fitAddon);

        // Open terminal in DOM element
        term.open(document.getElementById(config.element));
        fitAddon.fit();

        // Store terminal instance
        terminals[config.id] = term;

        // Write welcome message
        term.writeln(`\x1b[1;32m╔════════════════════════════════════════════════════╗\x1b[0m`);
        term.writeln(`\x1b[1;32m║   WebApp Firewall Simulator - ${config.title.padEnd(18)} ║\x1b[0m`);
        term.writeln(`\x1b[1;32m║   Educational Network Security Tool              ║\x1b[0m`);
        term.writeln(`\x1b[1;32m╚════════════════════════════════════════════════════╝\x1b[0m`);
        term.writeln('');
        
        if (config.id === 'firewall') {
            term.writeln(`\x1b[1;33mFirewall Configuration Terminal\x1b[0m`);
            term.writeln(`Configure iptables rules to control all network traffic.`);
            term.writeln('');
            term.writeln(`\x1b[36mCommon commands:\x1b[0m`);
            term.writeln(`  iptables -A OUTPUT -s 192.168.10.0/24 -p tcp --dport 80 -j ACCEPT`);
            term.writeln(`  iptables -A INPUT -s 192.168.20.0/24 -d 192.168.30.10 -j ACCEPT`);
            term.writeln(`  iptables -L -v`);
        } else {
            term.writeln(`\x1b[1;33mConfigure your network:\x1b[0m`);
            term.writeln(`  $ \x1b[36mifconfig set ip <ip_address>\x1b[0m`);
            term.writeln('');
            term.writeln(`\x1b[1;33mTest connectivity:\x1b[0m`);
            term.writeln(`  $ \x1b[36mping <target_ip>\x1b[0m`);
            term.writeln(`  $ \x1b[36mnmap -p 80,443 <target_ip>\x1b[0m`);
        }
        term.writeln('');
        term.writeln(`Type \x1b[1;33mhelp\x1b[0m for all available commands.`);
        term.writeln('');
        term.write(`\x1b[1;36m${config.id}@firewall\x1b[0m:\x1b[1;34m~\x1b[0m$ `);

        // Handle terminal input
        term.onData(data => {
            handleTerminalInput(config.id, data, term);
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            fitAddon.fit();
        });
    });
}

// Handle terminal input
function handleTerminalInput(terminalId, data, term) {
    const code = data.charCodeAt(0);

    // Handle Enter key
    if (code === 13) {
        term.writeln('');
        const command = commandBuffers[terminalId].trim();
        
        if (command) {
            // Send command to server
            socket.emit('command', {
                terminal: terminalId,
                command: command
            });
        } else {
            // Empty command, just show prompt
            term.write(`\x1b[1;36m${terminalId}@firewall\x1b[0m:\x1b[1;34m~\x1b[0m$ `);
        }
        
        commandBuffers[terminalId] = '';
        return;
    }

    // Handle Backspace
    if (code === 127) {
        if (commandBuffers[terminalId].length > 0) {
            commandBuffers[terminalId] = commandBuffers[terminalId].slice(0, -1);
            term.write('\b \b');
        }
        return;
    }

    // Handle Ctrl+C
    if (code === 3) {
        term.writeln('^C');
        commandBuffers[terminalId] = '';
        term.write(`\x1b[1;36m${terminalId}@firewall\x1b[0m:\x1b[1;34m~\x1b[0m$ `);
        return;
    }

    // Handle Ctrl+L (clear)
    if (code === 12) {
        term.clear();
        term.write(`\x1b[1;36m${terminalId}@firewall\x1b[0m:\x1b[1;34m~\x1b[0m$ `);
        return;
    }

    // Handle printable characters
    if (code >= 32 && code < 127) {
        commandBuffers[terminalId] += data;
        term.write(data);
    }
}

// Socket.IO event handlers
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('connected', (data) => {
    console.log('Server message:', data.data);
});

let sessionTimer = null;
socket.on('session_initialized', (data) => {
    console.log(`Session initialized with a lifetime of ${data.lifetime} seconds.`);
    
    // Clear any existing timer
    if (sessionTimer) {
        clearTimeout(sessionTimer);
    }
    
    // Set a timer to alert the user and reload the page upon session expiry
    sessionTimer = setTimeout(() => {
        alert("Your 45-minute session has expired. The simulator will now reset.");
        location.reload();
    }, data.lifetime * 1000); // Convert seconds to milliseconds
});

socket.on('output', (data) => {
    const term = terminals[data.terminal];
    if (term) {
        // Write output
        const output = data.output;
        const lines = output.split('\n');
        lines.forEach((line, index) => {
            if (line || index < lines.length - 1) {
                term.writeln(line);
            }
        });
        
        // Show prompt
        term.write(`\x1b[1;36m${data.terminal}@firewall\x1b[0m:\x1b[1;34m~\x1b[0m$ `);
    }
});

socket.on('clear', (data) => {
    const term = terminals[data.terminal];
    if (term) {
        term.clear();
        term.write(`\x1b[1;36m${data.terminal}@firewall\x1b[0m:\x1b[1;34m~\x1b[0m$ `);
    }
});

socket.on('update_ip_display', (data) => {
    const displayElement = document.getElementById(`${data.terminal}-display-ip`);
    if (displayElement) {
        displayElement.textContent = data.ip;
    }
    
    // Update network display
    const networkElement = document.getElementById(`${data.terminal}-network`);
    if (networkElement && data.network) {
        networkElement.textContent = `Network: ${data.network}`;
    }
    
    // Update terminal title to show IP
    const titleElement = document.getElementById(`${data.terminal}-terminal-title`);
    if (titleElement) {
        const baseTitles = {
            'insider': 'LAN1 - Internal PC',
            'outsider': 'LAN2 - External PC',
            'dmz': 'DMZ - Web Server'
        };
        titleElement.textContent = `${baseTitles[data.terminal]} (${data.ip})`;
    }
});

socket.on('new_log', (log) => {
    // Apply current filter before adding
    const shouldDisplay = currentLogFilter === 'all' || 
        (currentLogFilter === 'blocked' && ['DROP', 'REJECT'].includes(log.action)) ||
        (currentLogFilter === 'allowed' && log.action === 'ACCEPT') ||
        (currentLogFilter === 'warnings' && (log.category === 'warning' || log.action === 'WARNING'));
    
    if (shouldDisplay) {
        addLogEntry(log);
    }
    
    // Update stats by getting latest log data
    socket.emit('get_logs');
});

socket.on('logs_data', (data) => {
    const logsContent = document.getElementById('logs-content');
    if (!logsContent) return;
    logsContent.innerHTML = '';
    
    updateLogStats(data.stats);
    
    const logsToDisplay = data.logs || [];
    if (logsToDisplay.length === 0) {
        logsContent.innerHTML = '<div class="no-logs">No firewall logs yet.</div>';
        return;
    }
    
    const filteredLogs = filterLogsByCategory(logsToDisplay, currentLogFilter);
    
    if (filteredLogs.length === 0) {
        logsContent.innerHTML = `<div class="no-logs">No logs in "${currentLogFilter}" category.</div>`;
        return;
    }
    
    filteredLogs.forEach(log => {
        addLogEntry(log);
    });
});

socket.on('rules_data', (data) => {
    const blob = new Blob([data.rules], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    
    // Create timestamped filename e.g., 20251130094500.waf
    const d = new Date();
    const timestamp = `${d.getFullYear()}${(d.getMonth()+1).toString().padStart(2, '0')}${d.getDate().toString().padStart(2, '0')}` +
                    `${d.getHours().toString().padStart(2, '0')}${d.getMinutes().toString().padStart(2, '0')}${d.getSeconds().toString().padStart(2, '0')}`;
    a.download = `${timestamp}.waf`;
    
    a.click();
    URL.revokeObjectURL(url);
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    
    // Show disconnection message in all terminals
    Object.keys(terminals).forEach(terminalId => {
        const term = terminals[terminalId];
        if (term) {
            term.writeln('');
            term.writeln('\x1b[1;31m[Connection lost. Attempting to reconnect...]\x1b[0m');
        }
    });
});

socket.on('reconnect', () => {
    console.log('Reconnected to server');
    
    // Show reconnection message in all terminals
    Object.keys(terminals).forEach(terminalId => {
        const term = terminals[terminalId];
        if (term) {
            term.writeln('\x1b[1;32m[Reconnected successfully]\x1b[0m');
            term.write(`\x1b[1;36m${terminalId}@firewall\x1b[0m:\x1b[1;34m~\x1b[0m$ `);
        }
    });
});

// Download rules functionality
function downloadRules() {
    socket.emit('get_rules');
}

// Upload rules functionality
function triggerUpload() {
    document.getElementById('rule-file-input').click();
}

function setupUploadListener() {
    const fileInput = document.getElementById('rule-file-input');
    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (!file) {
            return;
        }
        if (!file.name.endsWith('.waf')) {
            alert("Invalid file type. Please select a .waf file.");
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            socket.emit('load_rules_from_script', { script: content });
            // Add a visual confirmation
            const firewallTerminal = terminals['firewall'];
            if(firewallTerminal) {
                firewallTerminal.writeln('');
                firewallTerminal.writeln('\x1b[1;32mRules loaded from file. Run "iptables -L" to see them.\x1b[0m');
                firewallTerminal.write(`\x1b[1;36mfirewall@firewall\x1b[0m:\x1b[1;34m~\x1b[0m$ `);
            }
        };
        reader.readAsText(file);

        // Reset the file input so the user can upload the same file again if needed
        event.target.value = '';
    });
}

// Toggle logs panel
function toggleLogs() {
    const logsPanel = document.getElementById('logs-panel');
    logsPanel.classList.toggle('active');
    
    if (logsPanel.classList.contains('active')) {
        loadLogs();
    }
}

// Current log filter
let currentLogFilter = 'all';

// Load logs from server
function loadLogs() {
    socket.emit('get_logs');
}

function updateLogStats(stats) {
    document.getElementById('total-logs').textContent = stats.total || 0;
    document.getElementById('blocked-logs').textContent = stats.blocked || 0;
    document.getElementById('allowed-logs').textContent = stats.allowed || 0;
    document.getElementById('warning-logs').textContent = stats.warnings || 0;
}

function filterLogsByCategory(logs, category) {
    if (category === 'all') return logs;
    if (category === 'blocked') return logs.filter(l => ['DROP', 'REJECT'].includes(l.action));
    if (category === 'allowed') return logs.filter(l => l.action === 'ACCEPT');
    if (category === 'warnings') return logs.filter(l => l.category === 'warning' || l.action === 'WARNING');
    return logs;
}

function filterLogs(category) {
    currentLogFilter = category;
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Reload logs with filter
    loadLogs();
}

socket.on('raw_logs_data', (data) => {
    const blob = new Blob([data.logs], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `firewall_logs_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

function downloadLogs() {
    socket.emit('get_raw_logs');
}

// Add log entry to display
function addLogEntry(log) {
    const logsContent = document.getElementById('logs-content');
    if (!logsContent) return;
    
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    
    // Determine log type for styling
    const action = log.action.toLowerCase();
    const category = log.category;

    if (category === 'warning' || action === 'warning') {
        logEntry.classList.add('log-warning');
    } else if (action === 'drop' || action === 'reject') {
        logEntry.classList.add('log-blocked');
    } else if (action === 'accept') {
        logEntry.classList.add('log-allowed');
    } else if (category === 'info') {
        logEntry.classList.add('log-info'); // A new style might be needed for this
    }
    
    const timestamp = new Date(log.timestamp).toLocaleTimeString();
    
    let detailsHtml = '';
    if (action === 'warning' || category === 'info') {
        detailsHtml = `<div class="log-details">ℹ️ ${log.rule || log.details}</div>`;
    } else {
        detailsHtml = `
            <div class="log-details">
                ${log.source} → ${log.destination} (${log.protocol.toUpperCase()}${log.port && log.port !== 'None' ? ':' + log.port : ''})
            </div>
            ${log.rule ? `<div class="log-rule">Rule: ${log.rule}</div>` : ''}
            ${log.warning ? `<div class="log-warning-text">⚠️ ${log.warning}</div>` : ''}
        `;
    }
    
    logEntry.innerHTML = `
        <div class="log-time">${timestamp}</div>
        <div class="log-action ${action}">${log.action}</div>
        ${detailsHtml}
    `;
    
    logsContent.appendChild(logEntry);
    logsContent.scrollTop = logsContent.scrollHeight;
}

// Clear logs
function clearLogs() {
    if (!confirm("Are you sure you want to clear all logs and statistics? This action cannot be undone.")) {
        return;
    }
    socket.emit('clear_logs');
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    initializeTerminals();
    setupUploadListener();
});
