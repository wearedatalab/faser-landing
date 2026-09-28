<?php
/**
 * FASER GROUP — receptor del formulario de contacto.
 * Sin dependencias (PHP 7.4+). Envía cada lead por correo a los destinatarios de config.php,
 * guarda una copia en _data/leads.csv y aplica antispam (honeypot, tiempo mínimo, límite por IP,
 * control de origen y de enlaces).
 *
 * Envío: SMTP si config.php lo tiene activo (recomendado), si no la función mail() del hosting.
 */
declare(strict_types=1);
// Ningún aviso de PHP debe mezclarse con la respuesta JSON (se registran en el log del servidor)
ini_set('display_errors', '0');
error_reporting(E_ALL);
header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');
header('Cache-Control: no-store');

function respond(int $code, array $body): void { http_response_code($code); echo json_encode($body, JSON_UNESCAPED_UNICODE); exit; }

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') respond(405, ['ok' => false, 'error' => 'method']);

$cfgFile = __DIR__ . '/config.php';
if (!is_file($cfgFile)) respond(500, ['ok' => false, 'error' => 'config']);
$cfg = require $cfgFile;
date_default_timezone_set($cfg['timezone'] ?? 'America/Guyana');

$dataDir = __DIR__ . '/_data';
if (!is_dir($dataDir)) @mkdir($dataDir, 0750, true);

/* ---------- utilidades ---------- */
function field(string $k, int $max = 200): string {
    $v = isset($_POST[$k]) ? (string)$_POST[$k] : '';
    $v = trim(str_replace("\0", '', $v));
    if (function_exists('mb_substr')) $v = mb_substr($v, 0, $max, 'UTF-8'); else $v = substr($v, 0, $max);
    return $v;
}
function oneLine(string $v): string { return trim(preg_replace('/[\r\n\t]+/', ' ', $v)); }
function h(string $v): string { return htmlspecialchars($v, ENT_QUOTES, 'UTF-8'); }
function encHeader(string $v): string { return '=?UTF-8?B?' . base64_encode($v) . '?='; }
function logLine(string $dir, string $msg): void { @file_put_contents($dir . '/mail.log', date('c') . ' ' . $msg . "\n", FILE_APPEND | LOCK_EX); }

$ip = $_SERVER['HTTP_CF_CONNECTING_IP'] ?? ($_SERVER['REMOTE_ADDR'] ?? '0.0.0.0');

/* ---------- antispam ---------- */
// 1) honeypot: los humanos no ven el campo "website"
if (field('website') !== '') respond(200, ['ok' => true]);
// 2) tiempo mínimo entre la carga de la página y el envío (bots envían al instante)
$t = (int)field('t', 20);
$elapsed = (int)(microtime(true) * 1000) - $t;
if ($t <= 0 || $elapsed < 3000 || $elapsed > 86400000) respond(200, ['ok' => true]);
// 3) el envío debe venir de este mismo sitio
$origin = $_SERVER['HTTP_ORIGIN'] ?? ($_SERVER['HTTP_REFERER'] ?? '');
$host = $_SERVER['HTTP_HOST'] ?? '';
if ($origin !== '' && $host !== '' && parse_url($origin, PHP_URL_HOST) !== preg_replace('/:\d+$/', '', $host)) respond(403, ['ok' => false, 'error' => 'origin']);
// 4) límite por IP
$limit = (int)($cfg['rate_limit_per_hour'] ?? 5);
$rlFile = $dataDir . '/ratelimit.json';
$fh = @fopen($rlFile, 'c+');
if ($fh && flock($fh, LOCK_EX)) {
    $raw = stream_get_contents($fh); $rl = $raw ? (json_decode($raw, true) ?: []) : [];
    $now = time(); $key = hash('sha256', $ip);
    foreach ($rl as $k => $list) { $rl[$k] = array_values(array_filter($list, function ($x) use ($now) { return $x > $now - 3600; })); if (!$rl[$k]) unset($rl[$k]); }
    if (count($rl[$key] ?? []) >= $limit) { flock($fh, LOCK_UN); fclose($fh); respond(429, ['ok' => false, 'error' => 'rate']); }
    $rl[$key][] = $now;
    ftruncate($fh, 0); rewind($fh); fwrite($fh, json_encode($rl)); fflush($fh); flock($fh, LOCK_UN); fclose($fh);
}

/* ---------- validación ---------- */
$lead = [
    'name'     => oneLine(field('name', 120)),
    'email'    => oneLine(field('email', 160)),
    'phone'    => oneLine(field('phone', 40)),
    'company'  => oneLine(field('company', 120)),
    'based'    => oneLine(field('based', 60)),
    'pref'     => oneLine(field('contact_pref', 30)),
    'interest' => oneLine(field('interest', 80)),
    'message'  => field('message', 3000),
    'lang'     => field('lang', 5) === 'es' ? 'es' : 'en',
    'page'     => oneLine(field('page', 500)),
    'referrer' => oneLine(field('referrer', 500)),
];
$errors = [];
if (strlen($lead['name']) < 2) $errors[] = 'name';
if (!filter_var($lead['email'], FILTER_VALIDATE_EMAIL)) $errors[] = 'email';
if (strlen(preg_replace('/\D/', '', $lead['phone'])) < 7) $errors[] = 'phone';
if ($lead['based'] === '') $errors[] = 'based';
if ($lead['interest'] === '') $errors[] = 'interest';
if (strlen(trim($lead['message'])) < 2) $errors[] = 'message';
if (field('consent', 10) === '') $errors[] = 'consent';
if ($errors) respond(400, ['ok' => false, 'error' => 'validation', 'fields' => $errors]);
// 5) mensajes llenos de enlaces = spam
if (preg_match_all('~https?://|www\.~i', $lead['message']) > 2) respond(200, ['ok' => true]);

/* ---------- copia de respaldo (nunca se pierde un lead) ---------- */
$csv = $dataDir . '/leads.csv';
$isNew = !is_file($csv);
if ($out = @fopen($csv, 'a')) {
    if (flock($out, LOCK_EX)) {
        if ($isNew) fputcsv($out, ['date', 'name', 'email', 'phone', 'company', 'based', 'contact_pref', 'interest', 'message', 'lang', 'page', 'referrer', 'ip'], ',', '"', '');
        $row = [date('Y-m-d H:i:s'), $lead['name'], $lead['email'], $lead['phone'], $lead['company'], $lead['based'], $lead['pref'], $lead['interest'], $lead['message'], $lead['lang'], $lead['page'], $lead['referrer'], $ip];
        // evita fórmulas al abrir el CSV en Excel
        $row = array_map(function ($v) { return preg_match('/^[=+\-@]/', (string)$v) ? "'" . $v : $v; }, $row);
        fputcsv($out, $row, ',', '"', ''); flock($out, LOCK_UN);
    }
    fclose($out);
}

/* ---------- correo ---------- */
$rows = [
    ['Nombre / Name', $lead['name']], ['Correo / Email', $lead['email']], ['Teléfono / Phone', $lead['phone']],
    ['Empresa / Company', $lead['company'] ?: '—'], ['Ubicación / Based in', $lead['based']], ['Contacto preferido / Best way to reach', $lead['pref']],
    ['Interés / Interested in', $lead['interest']], ['Idioma de la página / Page language', strtoupper($lead['lang'])],
];
$subject = ($cfg['subject_prefix'] ?? 'Nuevo lead FASER') . ' · ' . $lead['interest'] . ' · ' . $lead['name'];
$html = '<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#29292c;max-width:640px">'
    . '<p style="margin:0 0 4px;font-size:12px;letter-spacing:2px;color:#c8102e"><b>FASER GROUP · LANDING</b></p>'
    . '<h2 style="margin:0 0 16px;font-size:20px">Nuevo lead / New lead</h2><table cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%">';
foreach ($rows as $r) $html .= '<tr><td style="border-bottom:1px solid #e3e6ea;color:#6b6d72;width:42%">' . h($r[0]) . '</td><td style="border-bottom:1px solid #e3e6ea"><b>' . h($r[1]) . '</b></td></tr>';
$html .= '</table><p style="margin:18px 0 6px;color:#6b6d72">Mensaje / Message</p><div style="padding:12px 14px;background:#f1f5f8;border-left:3px solid #e30613">' . nl2br(h($lead['message'])) . '</div>'
    . '<p style="margin:18px 0 0;font-size:12px;color:#6b6d72">Página / Page: ' . h($lead['page']) . ($lead['referrer'] ? '<br>Referencia / Referrer: ' . h($lead['referrer']) : '') . '<br>' . date('Y-m-d H:i T') . '</p>'
    . '<p style="margin:14px 0 0;font-size:12px;color:#6b6d72">Responde este correo para escribirle directamente al contacto. / Reply to this email to answer the lead directly.</p></div>';
$text = "Nuevo lead / New lead — FASER GROUP\n\n";
foreach ($rows as $r) $text .= $r[0] . ': ' . $r[1] . "\n";
$text .= "\nMensaje / Message:\n" . $lead['message'] . "\n\nPágina / Page: " . $lead['page'] . "\n" . date('Y-m-d H:i T') . "\n";

$to = array_values(array_filter(array_map('trim', (array)($cfg['to'] ?? [])), function ($e) { return filter_var($e, FILTER_VALIDATE_EMAIL); }));
if (!$to) { logLine($dataDir, 'ERROR sin destinatarios en config.php'); respond(500, ['ok' => false, 'error' => 'config']); }
$fromEmail = $cfg['from_email'] ?? ('no-reply@' . preg_replace('/^www\./', '', preg_replace('/:\d+$/', '', $host)));
$fromName = $cfg['from_name'] ?? 'FASER GROUP Website';

$boundary = 'b' . bin2hex(random_bytes(12));
$body = "--$boundary\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($text))
      . "--$boundary\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($html)) . "--$boundary--\r\n";
$replyName = encHeader($lead['name']);
$headers = [
    'From: ' . encHeader($fromName) . " <$fromEmail>",
    "Reply-To: $replyName <{$lead['email']}>",
    'MIME-Version: 1.0',
    "Content-Type: multipart/alternative; boundary=\"$boundary\"",
    'X-Mailer: FASER-Landing',
];
if (!empty($cfg['bcc'])) $headers[] = 'Bcc: ' . implode(', ', (array)$cfg['bcc']);

$smtp = $cfg['smtp'] ?? [];
if (!empty($smtp['enabled'])) {
    $err = smtpSend($smtp, $fromEmail, array_merge($to, (array)($cfg['bcc'] ?? [])),
        array_merge(['Date: ' . date('r'), 'To: ' . implode(', ', $to), 'Subject: ' . encHeader($subject), 'Message-ID: <' . bin2hex(random_bytes(10)) . '@' . substr(strrchr($fromEmail, '@'), 1) . '>'],
            array_filter($headers, function ($x) { return stripos($x, 'Bcc:') !== 0; })), $body);
    $sent = $err === '';
    if (!$sent) logLine($dataDir, 'SMTP ' . $err);
} else {
    $sent = @mail(implode(', ', $to), encHeader($subject), $body, implode("\r\n", $headers), '-f' . $fromEmail);
    if (!$sent) logLine($dataDir, 'mail() devolvió false');
}
// El lead ya quedó guardado en leads.csv: aunque el correo falle, se responde ok para no perder al contacto
respond(200, ['ok' => true, 'mail' => $sent]);

/* ---------- cliente SMTP mínimo (SSL 465 o STARTTLS 587) ---------- */
function smtpSend(array $s, string $from, array $rcpts, array $headers, string $body): string {
    $host = $s['host'] ?? ''; $port = (int)($s['port'] ?? 465); $secure = strtolower($s['secure'] ?? 'ssl');
    $ctx = stream_context_create(['ssl' => ['verify_peer' => true, 'verify_peer_name' => true]]);
    $fp = @stream_socket_client(($secure === 'ssl' ? 'ssl://' : 'tcp://') . "$host:$port", $en, $es, 20, STREAM_CLIENT_CONNECT, $ctx);
    if (!$fp) return "conexión $host:$port: $es";
    stream_set_timeout($fp, 20);
    $read = function () use ($fp) { $d = ''; while (($l = fgets($fp, 515)) !== false) { $d .= $l; if (strlen($l) < 4 || $l[3] === ' ') break; } return $d; };
    $cmd = function (string $c, array $okCodes) use ($fp, $read) { if ($c !== '') fwrite($fp, $c . "\r\n"); $r = $read(); return in_array((int)substr($r, 0, 3), $okCodes, true) ? '' : trim($c === '' ? $r : explode(' ', $c)[0] . ' → ' . $r); };
    $ehlo = 'EHLO ' . (gethostname() ?: 'localhost');
    if ($e = $cmd('', [220])) return $e;
    if ($e = $cmd($ehlo, [250])) return $e;
    if ($secure === 'tls') {
        if ($e = $cmd('STARTTLS', [220])) return $e;
        if (!stream_socket_enable_crypto($fp, true, STREAM_CRYPTO_METHOD_TLS_CLIENT)) return 'STARTTLS falló';
        if ($e = $cmd($ehlo, [250])) return $e;
    }
    if (!empty($s['user'])) {
        if ($e = $cmd('AUTH LOGIN', [334])) return $e;
        if ($e = $cmd(base64_encode($s['user']), [334])) return $e;
        if ($e = $cmd(base64_encode($s['pass'] ?? ''), [235])) return 'AUTH rechazada (usuario/clave SMTP)';
    }
    if ($e = $cmd("MAIL FROM:<$from>", [250])) return $e;
    foreach ($rcpts as $r) if ($e = $cmd("RCPT TO:<$r>", [250, 251])) return $e;
    if ($e = $cmd('DATA', [354])) return $e;
    $msg = implode("\r\n", $headers) . "\r\n\r\n" . $body;
    $msg = preg_replace('/^\./m', '..', $msg);
    if ($e = $cmd($msg . "\r\n.", [250])) return $e;
    $cmd('QUIT', [221]); fclose($fp);
    return '';
}
