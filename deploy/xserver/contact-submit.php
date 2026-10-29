<?php
declare(strict_types=1);

// Xserver's local mail service sends to this fixed address. Visitor input is
// used only in the message body and a validated Reply-To header.
const FORMUS_RECIPIENT = 'info@formus.jp';
const FORMUS_SENDER = 'info@formus.jp';
const FORMUS_COOLDOWN = 60;

ini_set('display_errors', '0');
header('Content-Type: application/json; charset=UTF-8');
header('Cache-Control: no-store, private');
header('Pragma: no-cache');
header('X-Content-Type-Options: nosniff');
header('X-Robots-Tag: noindex, nofollow');

function respond(int $status, string $message, array $extra = []): void
{
    http_response_code($status);
    echo json_encode(['ok' => $status < 400, 'message' => $message] + $extra, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function token(): string
{
    if (!isset($_SESSION['csrf'], $_SESSION['csrf_time']) || time() - $_SESSION['csrf_time'] > 7200) {
        $_SESSION['csrf'] = bin2hex(random_bytes(32));
        $_SESSION['csrf_time'] = time();
    }
    return $_SESSION['csrf'];
}

function textField(string $name, int $limit, bool $required = true, bool $multiline = false): string
{
    $value = $_POST[$name] ?? '';
    if (!is_string($value) || !preg_match('//u', $value)) {
        respond(422, '入力内容をご確認ください。');
    }
    $value = trim(str_replace(["\r\n", "\r"], "\n", $value));
    if (($required && $value === '') || preg_match_all('/./us', $value) > $limit || preg_match('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/', $value) || (!$multiline && str_contains($value, "\n"))) {
        respond(422, $name . 'の入力内容をご確認ください。');
    }
    return $value;
}

try {
    $method = $_SERVER['REQUEST_METHOD'] ?? '';
    if (!in_array($method, ['GET', 'POST'], true)) {
        header('Allow: GET, POST');
        respond(405, 'この操作には対応していません。');
    }
    $secure = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || ($_SERVER['SERVER_PORT'] ?? '') === '443';
    ini_set('session.use_strict_mode', '1');
    session_name('FORMUS_CONTACT');
    session_set_cookie_params(['lifetime' => 0, 'path' => '/', 'secure' => $secure, 'httponly' => true, 'samesite' => 'Strict']);
    if (!session_start()) {
        throw new RuntimeException('Session unavailable');
    }
    if ($method === 'GET') {
        respond(200, '', ['csrf' => token()]);
    }
    // Browser submissions must come from this site's own origin. CORS is not
    // enabled; the cookie and CSRF token are required as well.
    $expectedOrigin = ($secure ? 'https://' : 'http://') . strtolower($_SERVER['HTTP_HOST'] ?? '');
    if (strtolower($_SERVER['HTTP_ORIGIN'] ?? '') !== $expectedOrigin) {
        respond(403, 'ページを再読み込みして、もう一度お試しください。');
    }
    if ((int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > 32768 || !empty($_FILES)) {
        respond(413, '送信内容が大きすぎます。');
    }
    $csrf = $_POST['csrf'] ?? '';
    if (!is_string($csrf) || !isset($_SESSION['csrf'], $_SESSION['csrf_time']) || time() - $_SESSION['csrf_time'] > 7200 || !hash_equals($_SESSION['csrf'], $csrf)) {
        respond(403, '入力画面の有効期限が切れました。もう一度送信ボタンを押してください。');
    }
    if (($_POST['website'] ?? '') !== '') {
        respond(422, '入力内容をご確認ください。');
    }

    $fields = [
        'お問い合わせ種別' => textField('お問い合わせ種別', 30),
        'ご希望の連絡方法' => textField('ご希望の連絡方法', 10),
        '会社名' => textField('会社名', 200),
        'お名前' => textField('お名前', 100),
        'フリガナ' => textField('フリガナ', 100),
        'email' => textField('email', 254),
        '電話番号' => textField('電話番号', 50),
        'お問い合わせ内容' => textField('お問い合わせ内容', 500, false, true),
    ];
    if (!in_array($fields['お問い合わせ種別'], ['事業内容について', '採用について', '協業について', 'その他'], true) || !in_array($fields['ご希望の連絡方法'], ['メール', '電話'], true)) {
        respond(422, 'お問い合わせ種別と連絡方法を選択してください。');
    }
    if (!filter_var($fields['email'], FILTER_VALIDATE_EMAIL)) {
        respond(422, 'メールアドレスをご確認ください。');
    }
    if (($_POST['個人情報の取り扱い'] ?? '') !== '同意する') {
        respond(422, '個人情報の取り扱いへの同意が必要です。');
    }

    // Limit accepted submissions across sessions from the same IP. The private
    // temporary files contain only a hashed key, timestamps and counters.
    $directory = sys_get_temp_dir() . '/formus-contact-' . substr(hash('sha256', __DIR__), 0, 20);
    if (!is_dir($directory) && !@mkdir($directory, 0700, true) && !is_dir($directory)) {
        throw new RuntimeException('Rate storage unavailable');
    }
    $key = hash('sha256', $_SERVER['REMOTE_ADDR'] ?? 'unknown');
    $lock = @fopen($directory . '/' . $key, 'c+');
    if ($lock === false || !flock($lock, LOCK_EX)) {
        throw new RuntimeException('Rate lock unavailable');
    }
    $state = json_decode(stream_get_contents($lock), true) ?: [];
    $now = time();
    if ($now - (int) ($state['sent'] ?? 0) < FORMUS_COOLDOWN) {
        header('Retry-After: ' . FORMUS_COOLDOWN);
        respond(429, '続けて送信する場合は、1分ほどお待ちください。');
    }
    if ($now - (int) ($state['window'] ?? 0) >= 900) {
        $state['window'] = $now;
        $state['attempts'] = 0;
    }
    if ((int) ($state['attempts'] ?? 0) >= 10) {
        header('Retry-After: 900');
        respond(429, '送信回数の上限に達しました。しばらくしてからお試しください。');
    }
    $state['attempts'] = (int) ($state['attempts'] ?? 0) + 1;
    rewind($lock);
    ftruncate($lock, 0);
    if (fwrite($lock, json_encode($state)) === false || !fflush($lock)) {
        throw new RuntimeException('Rate write unavailable');
    }

    $body = "FORMUSのウェブサイトからお問い合わせがありました。\n\n";
    foreach ($fields as $label => $value) {
        $body .= '【' . ($label === 'email' ? 'メールアドレス' : $label) . "】\n" . ($value === '' ? '（未入力）' : $value) . "\n\n";
    }
    $body .= "個人情報の取り扱い：同意済み\n";
    $subject = '=?UTF-8?B?' . base64_encode('【FORMUS】お問い合わせ') . '?=';
    $headers = [
        'MIME-Version' => '1.0',
        'Content-Type' => 'text/plain; charset=UTF-8',
        'Content-Transfer-Encoding' => 'quoted-printable',
        'From' => 'FORMUS <' . FORMUS_SENDER . '>',
        'Reply-To' => $fields['email'],
    ];
    if (!function_exists('mail') || !@mail(FORMUS_RECIPIENT, $subject, quoted_printable_encode($body), $headers, '-f' . FORMUS_SENDER)) {
        error_log('FORMUS contact: mail transport unavailable');
        respond(503, '送信できませんでした。時間をおいてお試しいただくか、info@formus.jpへメールでご連絡ください。');
    }
    $state['sent'] = $now;
    rewind($lock);
    ftruncate($lock, 0);
    fwrite($lock, json_encode($state));
    fflush($lock);
    flock($lock, LOCK_UN);
    fclose($lock);
    unset($_SESSION['csrf'], $_SESSION['csrf_time']);
    respond(200, 'お問い合わせを受け付けました。2〜3営業日以内に、担当者よりご連絡いたします。');
} catch (Throwable $error) {
    error_log('FORMUS contact: request could not be completed');
    respond(503, '送信の準備ができませんでした。時間をおいてお試しいただくか、info@formus.jpへメールでご連絡ください。');
}
