// BOOPING App - Boop Interactions
// Created by Claude Opus 4.5

// Store favorite IDs for quick lookup
let favoriteIds = new Set();

// Paw emoji mapping
const pawEmojis = {
    'default': '🐾',
    'sparkle': '✨',
    'ghost': '👻',
    'fire': '🔥',
    'rainbow': '🌈',
    'star': '⭐',
    'heart': '💖',
    'galaxy': '🌌',
    'skeleton': '💀',
    'alien': '👽',
    'robot': '🤖',
    'cat': '🐱',
    'moon': '🌙',
    'sun': '☀️',
    'lightning': '⚡',
    'snowflake': '❄️'
};

// Check if user was active recently
function getActivityClass(lastActive) {
    if (!lastActive) return '';
    const now = new Date();
    const active = new Date(lastActive);
    const diffMinutes = (now - active) / (1000 * 60);

    if (diffMinutes < 5) return 'user-active';      // Active in last 5 min
    if (diffMinutes < 60) return 'user-recent';     // Active in last hour
    return '';
}

// Create a user card HTML
function createUserCard(user, isFavorite) {
    const starClass = isFavorite ? 'star-btn favorited' : 'star-btn';
    const starIcon = isFavorite ? '★' : '☆';
    const activityClass = getActivityClass(user.last_active);
    return `
        <div class="user-card ${activityClass}" style="--user-color: ${user.color_theme}" data-user-id="${user.id}">
            <button class="${starClass}" onclick="toggleFavorite(${user.id}, this)" title="Toggle favorite">
                ${starIcon}
            </button>
            <div class="user-info">
                <div class="user-display-name">${escapeHtml(user.display_name)}</div>
            </div>
            <button class="boop-btn" onclick="sendBoop(${user.id}, this)">
                BOOP
            </button>
        </div>
    `;
}

// Load all user sections
async function loadUsers() {
    try {
        // Load favorite IDs first
        const favIdsResponse = await fetch('/api/users/me/favorite-ids');
        const favIds = await favIdsResponse.json();
        favoriteIds = new Set(favIds);

        // Load all data in parallel
        const [usersResponse, favoritesResponse, mutualsResponse] = await Promise.all([
            fetch('/api/users'),
            fetch('/api/users/me/favorites'),
            fetch('/api/users/me/mutuals')
        ]);

        const allUsers = await usersResponse.json();
        const favorites = await favoritesResponse.json();
        const mutuals = await mutualsResponse.json();

        // Get IDs for filtering
        const favoriteUserIds = new Set(favorites.map(f => f.id));
        const mutualUserIds = new Set(mutuals.map(m => m.id));

        // Filter "everyone" to exclude favorites and mutuals
        const everyoneElse = allUsers.filter(u =>
            !favoriteUserIds.has(u.id) && !mutualUserIds.has(u.id)
        );

        // Render Favorites section
        const favoritesSection = document.getElementById('favorites-section');
        const favoritesList = document.getElementById('favorites-list');
        if (favorites.length > 0) {
            favoritesSection.style.display = 'block';
            favoritesList.innerHTML = favorites.map(user =>
                createUserCard(user, true)
            ).join('');
        } else {
            favoritesSection.style.display = 'none';
        }

        // Render Mutuals section
        const mutualsSection = document.getElementById('mutuals-section');
        const mutualsList = document.getElementById('mutuals-list');
        if (mutuals.length > 0) {
            mutualsSection.style.display = 'block';
            mutualsList.innerHTML = mutuals.map(user =>
                createUserCard(user, favoriteIds.has(user.id))
            ).join('');
        } else {
            mutualsSection.style.display = 'none';
        }

        // Render Everyone section
        const userList = document.getElementById('user-list');
        if (everyoneElse.length === 0 && favorites.length === 0 && mutuals.length === 0) {
            userList.innerHTML = '<div class="loading">No other boopers yet. Invite some friends!</div>';
        } else if (everyoneElse.length === 0) {
            userList.innerHTML = '<div class="loading">Everyone is either a favorite or boop buddy!</div>';
        } else {
            userList.innerHTML = everyoneElse.map(user =>
                createUserCard(user, favoriteIds.has(user.id))
            ).join('');
        }
    } catch (error) {
        console.error('Failed to load users:', error);
    }
}

// Toggle favorite status
async function toggleFavorite(userId, button) {
    const isFavorited = favoriteIds.has(userId);

    try {
        if (isFavorited) {
            await fetch(`/api/favorites/${userId}`, { method: 'DELETE' });
            favoriteIds.delete(userId);
            button.classList.remove('favorited');
            button.textContent = '☆';
        } else {
            await fetch(`/api/favorites/${userId}`, { method: 'POST' });
            favoriteIds.add(userId);
            button.classList.add('favorited');
            button.textContent = '★';
        }
        // Reload to update sections
        loadUsers();
    } catch (error) {
        console.error('Failed to toggle favorite:', error);
    }
}

// Load global stats
async function loadGlobalStats() {
    try {
        const response = await fetch('/api/stats/global');
        const stats = await response.json();
        updateGlobalCounter(stats.total_boops);
    } catch (error) {
        console.error('Failed to load global stats:', error);
    }
}

// Load my stats
async function loadMyStats() {
    try {
        const response = await fetch('/api/users/me/stats');
        const stats = await response.json();
        const myStats = document.getElementById('my-stats');
        if (myStats) {
            myStats.textContent = `${stats.boops_sent} sent / ${stats.boops_received} received`;
        }
    } catch (error) {
        console.error('Failed to load my stats:', error);
    }
}

// Load new boops since last login
async function loadNewBoops() {
    try {
        const response = await fetch('/api/users/me/new-boops');
        const boops = await response.json();

        if (boops.length > 0) {
            // Show the banner with total count
            document.getElementById('new-boops-banner').style.display = 'block';
            document.getElementById('new-boops-count').textContent = boops.length;

            // Aggregate by sender
            const grouped = {};
            boops.forEach(boop => {
                const senderId = boop.sender_id;
                if (!grouped[senderId]) {
                    grouped[senderId] = {
                        sender_name: boop.sender_name,
                        paw_style: boop.sender_paw || boop.paw_style,
                        count: 0,
                        latest: boop.created_at
                    };
                }
                grouped[senderId].count++;
                // Keep the most recent timestamp
                if (boop.created_at > grouped[senderId].latest) {
                    grouped[senderId].latest = boop.created_at;
                }
            });

            // Sort by count (most boops first)
            const sorted = Object.values(grouped).sort((a, b) => b.count - a.count);

            // Build the list showing count per sender
            const listHtml = sorted.map(sender => {
                const pawEmoji = pawEmojis[sender.paw_style] || '🐾';
                const countText = sender.count > 1 ? ` x${sender.count}` : '';
                return `
                    <div class="new-boop-item">
                        <span class="new-boop-paw">${pawEmoji}</span>
                        <span class="new-boop-sender">${escapeHtml(sender.sender_name)}</span>
                        <span class="new-boop-count">${countText}</span>
                    </div>
                `;
            }).join('');

            document.getElementById('new-boops-list').innerHTML = listHtml;
        }
    } catch (error) {
        console.error('Failed to load new boops:', error);
    }
}

// Send a boop
function sendBoop(recipientId, button) {
    // Animate button
    button.classList.add('booping');
    setTimeout(() => button.classList.remove('booping'), 300);

    // Create flying paw animation with user's selected paw style
    createFlyingPaw(button, typeof myPawStyle !== 'undefined' ? myPawStyle : 'default');

    // Send via socket (server uses current_user's paw_style)
    sendBoopViaSocket(recipientId);

    // Update my stats
    loadMyStats();
}

// Create flying paw animation
function createFlyingPaw(fromElement, pawStyle) {
    const paw = document.createElement('div');
    paw.className = 'flying-paw';
    paw.textContent = getPawEmoji(pawStyle);

    const rect = fromElement.getBoundingClientRect();
    paw.style.left = `${rect.left + rect.width / 2}px`;
    paw.style.top = `${rect.top}px`;

    document.getElementById('paw-container').appendChild(paw);

    setTimeout(() => paw.remove(), 800);
}

// Show incoming boop animation
function showIncomingBoop(sender) {
    const paw = document.createElement('div');
    paw.className = 'incoming-paw';
    paw.textContent = getPawEmoji(sender.paw_style);
    paw.style.left = '50%';
    paw.style.transform = 'translateX(-50%)';

    document.body.appendChild(paw);

    setTimeout(() => paw.remove(), 1000);
}

// Show notification
function showNotification(message, color) {
    const container = document.getElementById('notifications');
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.style.borderLeftColor = color || '#ff00ff';
    notification.innerHTML = `<div class="notification-text">${escapeHtml(message)}</div>`;

    container.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100px)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Show badge unlock
function showBadgeUnlock(badge) {
    const overlay = document.createElement('div');
    overlay.className = 'badge-unlock';
    overlay.innerHTML = `
        <div class="badge-unlock-icon">${badge.icon}</div>
        <div class="badge-unlock-title">${badge.name}</div>
        <div class="badge-unlock-desc">${badge.description}</div>
        ${badge.unlocks_paw ? `<div class="badge-unlock-desc">Unlocked: ${badge.unlocks_paw} paw!</div>` : ''}
    `;

    document.body.appendChild(overlay);

    setTimeout(() => {
        overlay.style.opacity = '0';
        setTimeout(() => overlay.remove(), 300);
    }, 2500);
}

// Update global counter
function updateGlobalCounter(count) {
    const counter = document.getElementById('total-boops');
    if (counter) {
        counter.textContent = formatNumber(count);
        counter.classList.add('counter-updated');
        setTimeout(() => counter.classList.remove('counter-updated'), 300);
    }
}

// Get paw emoji based on style
function getPawEmoji(style) {
    return pawEmojis[style] || '🐾';
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Format number with commas
function formatNumber(num) {
    return num.toLocaleString();
}
