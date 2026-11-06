<?php
declare(strict_types=1);
header('Content-Type: application/json');
header('Cache-Control: no-store');

const TTL = 300;
$dir = sys_get_temp_dir() . '/qrpair';
if (!is_dir($dir)) mkdir($dir, 0700, true);

function fail(int $code, string $msg): never {
    http_response_code($code);
    echo json_encode(['error' => $msg]);
    exit;
}

function file_for(string $id): string {
    global $dir;
    if (!preg_match('/^[a-f0-9]{32}$/', $id)) fail(400, 'id invalide');
    return "$dir/$id.json";
}

function load(string $f): ?array {
    if (!is_file($f)) return null;
    if (time() - filemtime($f) > TTL) { @unlink($f); return null; }
    return json_decode((string) file_get_contents($f), true);
}

$action = $_GET['action'] ?? '';
$body = json_decode((string) file_get_contents('php://input'), true) ?? [];

if ($action === 'create' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    foreach (glob("$dir/*.json") ?: [] as $f) {
        if (time() - filemtime($f) > TTL) @unlink($f);
    }
    $id = bin2hex(random_bytes(16));
    $rk = bin2hex(random_bytes(16));
    file_put_contents(file_for($id), json_encode(['rk' => hash('sha256', $rk), 'url' => null]), LOCK_EX);
    echo json_encode(['id' => $id, 'rk' => $rk, 'ttl' => TTL]);

} elseif ($action === 'send' && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $f = file_for((string) ($body['id'] ?? ''));
    $url = (string) ($body['url'] ?? '');
    $scheme = strtolower((string) parse_url($url, PHP_URL_SCHEME));
    if (strlen($url) > 2048 || !filter_var($url, FILTER_VALIDATE_URL) || !in_array($scheme, ['http', 'https'], true)) {
        fail(400, 'url invalide');
    }
    $s = load($f) ?? fail(404, 'session inconnue ou expirée');
    if ($s['url'] !== null) fail(409, 'déjà utilisée');
    $s['url'] = $url;
    file_put_contents($f, json_encode($s), LOCK_EX);
    echo json_encode(['ok' => true]);

} elseif ($action === 'poll' && $_SERVER['REQUEST_METHOD'] === 'GET') {
    $f = file_for((string) ($_GET['id'] ?? ''));
    $s = load($f) ?? fail(404, 'session inconnue ou expirée');
    if (!hash_equals($s['rk'], hash('sha256', (string) ($_GET['rk'] ?? '')))) fail(403, 'clé invalide');
    if ($s['url'] !== null) @unlink($f); // lecture unique
    echo json_encode(['url' => $s['url']]);

} else {
    fail(400, 'action inconnue');
}