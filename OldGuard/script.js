// --- 1. FETCH DATA FROM SERVER ---
async function fetchChain() {
    try {
        const res = await fetch('/api/chain');
        const data = await res.json();
        render(data);
    } catch (err) {
        console.error("Failed to connect to blockchain node:", err);
    }
}

// --- 2. RENDER UI ---
function render(data) {
    // Render Scores
    const scoreBody = document.getElementById('scoreTable');
    scoreBody.innerHTML = '';
    
    // Sort scores so highest trust is at the top
    const sortedScores = Object.entries(data.scores).sort(([,a],[,b]) => b - a);

    for (const [user, score] of sortedScores) {
        const row = document.createElement('tr');
        const isBanned = score < -1;
        row.innerHTML = `
            <td>${user} ${isBanned ? '🚫' : ''}</td>
            <td class="${isBanned ? 'banned' : ''}">${score}</td>
        `;
        scoreBody.appendChild(row);
    }

    // Render Chain
    const chainContainer = document.getElementById('chainContainer');
    chainContainer.innerHTML = '';
    
    // Reverse loop to show newest blocks first
    [...data.chain].reverse().forEach(block => {
        const div = document.createElement('div');
        div.className = `block ${block.index === 0 ? 'genesis' : ''}`;
        
        div.innerHTML = `
            <div style="display:flex; justify-content:space-between">
                <strong>BLOCK #${block.index}</strong>
                <span>Nonce: ${block.nonce}</span>
            </div>
            <div style="margin: 5px 0;">
                ${block.sender} ➔ ${block.receiver} 
                <span style="color:${block.amount > 0 ? '#10b981' : '#ef4444'}">
                    (${block.amount} Coins)
                </span>
            </div>
            <div class="hash">${block.hash}</div>
        `;
        chainContainer.appendChild(div);
    });
}

// --- 3. HANDLE MINING ---
async function mineBlock() {
    const sender = document.getElementById('sender').value;
    const receiver = document.getElementById('receiver').value;
    const amount = document.getElementById('amount').value;
    const btn = document.getElementById('mineBtn');
    const loader = document.getElementById('loader');

    if(!sender || !receiver || !amount) {
        alert("Please fill in all fields");
        return;
    }

    // UI Feedback (Disable button while mining)
    btn.disabled = true;
    loader.style.display = 'block';

    try {
        const res = await fetch('/api/mine', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ sender, receiver, amount })
        });

        const result = await res.json();
        
        if (res.status === 403) {
            alert("⛔ TRANSACTION REJECTED: " + result.error);
        } else {
            // Success: clear the amount field
            document.getElementById('amount').value = '';
        }

    } catch (err) {
        alert("Server Error: Check your Python console.");
    } finally {
        // Re-enable UI
        btn.disabled = false;
        loader.style.display = 'none';
        fetchChain(); // Refresh data immediately
    }
}

// Attach Event Listener to Button
document.getElementById('mineBtn').addEventListener('click', mineBlock);

// Initial Load
fetchChain();

// Auto-refresh every 3 seconds to keep UI in sync
setInterval(fetchChain, 3000);