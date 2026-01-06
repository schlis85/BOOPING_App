// BOOPING App - Socket.IO Client
// Created by Claude Opus 4.5

let socket = null;

function initSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('Connected to BOOPING server!');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });

    socket.on('boop_received', (data) => {
        showIncomingBoop(data.sender);
        showNotification(`${data.sender.display_name} booped you!`, data.sender.color_theme);
        // Update global counter when receiving a boop
        if (data.global_stats) {
            updateGlobalCounter(data.global_stats.total_boops);
        }
    });

    socket.on('boop_sent', (data) => {
        if (data.success) {
            console.log('Boop sent successfully!');
            // Update sender's global counter immediately
            if (data.global_stats) {
                updateGlobalCounter(data.global_stats.total_boops);
            }
        }
        if (data.new_badges && data.new_badges.length > 0) {
            data.new_badges.forEach(badge => showBadgeUnlock(badge));
        }
    });

    socket.on('global_stats_update', (stats) => {
        updateGlobalCounter(stats.total_boops);
    });
}

function sendBoopViaSocket(recipientId) {
    if (socket) {
        socket.emit('send_boop', {
            recipient_id: recipientId
            // Server uses sender's (current_user's) paw_style
        });
    }
}
