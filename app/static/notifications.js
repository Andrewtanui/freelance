// static/notifications.js

const notificationPopup = document.createElement('div');
notificationPopup.classList.add('notification-popup');
document.body.appendChild(notificationPopup);

const socket = io();

socket.on('connect', () => {
    const userId = '{{ session.get("user_id") }}'; 
    socket.emit('register', userId);
});

socket.on('notification', (data) => {
    const { event, data: notificationData } = data;

    if (event === 'profile_view') {
        showNotification(`${notificationData.viewer} viewed your profile.`);
    } else if (event === 'new_message') {
        showNotification(`New message from ${notificationData.sender}: ${notificationData.body}`);
    }
});

function showNotification(message) {
    notificationPopup.textContent = message;
    notificationPopup.style.display = 'block';
    setTimeout(() => {
        notificationPopup.style.display = 'none';
    }, 30000); // Hide the notification after 30 seconds
}