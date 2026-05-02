self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => clients.claim());

// Escucha mensajes desde la pagina para mostrar notificacion con sonido
self.addEventListener('message', e => {
    if (e.data && e.data.tipo === 'alarma') {
        self.registration.showNotification('\u23F1 Cabina Solar', {
            body: e.data.nombre
                ? '\u00A1La sesi\u00F3n de ' + e.data.nombre + ' ha terminado!'
                : '\u00A1La sesi\u00F3n ha terminado!',
            icon: '/static/icons/icon-192.png',
            badge: '/static/icons/icon-192.png',
            vibrate: [500, 300, 500, 300, 500],
            tag: 'alarma-cabina',
            renotify: true,
            requireInteraction: true
        });
    }
});

// Click en la notificacion: enfocar la PWA
self.addEventListener('notificationclick', e => {
    e.notification.close();
    e.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(lista => {
            if (lista.length > 0) {
                return lista[0].focus();
            }
            return clients.openWindow('/');
        })
    );
});
