<?php
/**
 * Configuración del formulario de FASER GROUP.
 * Copia este archivo como config.php (el paquete de producción ya lo trae) y ajusta los valores.
 * config.php está protegido por .htaccess: no se puede abrir desde el navegador.
 */
return [
    // Quién recibe los leads (uno o varios correos)
    'to' => ['__LEADS_TO__'],
    // Copia oculta opcional, por ejemplo ['otro@correo.com']
    'bcc' => [],

    // Remitente: debe ser un correo del dominio donde está alojada la landing (p. ej. no-reply@fasergroup.com).
    // El lead queda como "Responder a", así que al contestar el correo se le escribe directamente al contacto.
    'from_email' => '__FROM_EMAIL__',
    'from_name'  => 'FASER GROUP Website',
    'subject_prefix' => 'Nuevo lead FASER',

    // Envío por SMTP (recomendado: los correos no caen en spam).
    // Hostinger Email: host smtp.hostinger.com, puerto 465, secure 'ssl', usuario = el correo completo.
    // Si 'enabled' es false se usa la función mail() del hosting.
    'smtp' => [
        'enabled' => false,
        'host'    => 'smtp.hostinger.com',
        'port'    => 465,
        'secure'  => 'ssl',   // 'ssl' (465) o 'tls' (587)
        'user'    => '',
        'pass'    => '',
    ],

    'rate_limit_per_hour' => 5,          // envíos máximos por IP y hora
    'timezone' => 'America/Guyana',
];
