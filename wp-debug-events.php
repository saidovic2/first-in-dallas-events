<?php
/**
 * WordPress Events Debug Script
 * Upload to WordPress root, access once, then DELETE
 * URL: https://firstindallas.com/wp-debug-events.php
 */

// Load WordPress
define('WP_USE_THEMES', false);
require_once('./wp-load.php');

header('Content-Type: text/html; charset=utf-8');
echo '<html><head><title>Events Debug</title><style>
body { font-family: monospace; padding: 20px; background: #1e1e1e; color: #d4d4d4; }
h1 { color: #4ec9b0; }
h2 { color: #569cd6; margin-top: 30px; }
pre { background: #252526; padding: 15px; border-radius: 5px; overflow-x: auto; }
.success { color: #4ec9b0; }
.error { color: #f48771; }
.warning { color: #ce9178; }
</style></head><body>';

echo '<h1>🔍 Events CMS Debug Information</h1>';
echo '<hr>';

// 1. Check Plugin Settings
echo '<h2>1. Plugin Configuration</h2>';
$api_url = get_option('events_cms_api_url', 'NOT SET');
echo '<pre>';
echo 'API URL Setting: <span class="' . ($api_url === 'NOT SET' ? 'error' : 'success') . '">' . esc_html($api_url) . '</span>' . PHP_EOL;
echo '</pre>';

// 2. Test API Connection
echo '<h2>2. API Connection Test</h2>';
$test_url = $api_url . '/events?status=PUBLISHED&limit=5';
echo '<pre>';
echo 'Testing URL: ' . esc_html($test_url) . PHP_EOL;
echo 'Making request...' . PHP_EOL . PHP_EOL;

$response = wp_remote_get($test_url, array(
    'timeout' => 15,
    'headers' => array('Accept' => 'application/json')
));

if (is_wp_error($response)) {
    echo '<span class="error">❌ ERROR: ' . $response->get_error_message() . '</span>' . PHP_EOL;
} else {
    $status_code = wp_remote_retrieve_response_code($response);
    echo 'HTTP Status: <span class="' . ($status_code === 200 ? 'success' : 'error') . '">' . $status_code . '</span>' . PHP_EOL;
    
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    
    if (is_array($data)) {
        echo '<span class="success">✓ API Response OK</span>' . PHP_EOL;
        echo 'Events returned: <span class="success">' . count($data) . '</span>' . PHP_EOL . PHP_EOL;
        
        // Show first 3 events with dates
        echo '--- First 3 Events ---' . PHP_EOL;
        foreach (array_slice($data, 0, 3) as $idx => $event) {
            echo PHP_EOL . 'Event #' . ($idx + 1) . ':' . PHP_EOL;
            echo '  Title: ' . (isset($event['title']) ? $event['title'] : 'N/A') . PHP_EOL;
            echo '  Date: <span class="warning">' . (isset($event['start_at']) ? $event['start_at'] : 'N/A') . '</span>' . PHP_EOL;
            echo '  City: ' . (isset($event['city']) ? $event['city'] : 'N/A') . PHP_EOL;
        }
    } else {
        echo '<span class="error">❌ Invalid JSON response</span>' . PHP_EOL;
        echo 'Response preview: ' . substr($body, 0, 200) . '...' . PHP_EOL;
    }
}
echo '</pre>';

// 3. Check Current Time
echo '<h2>3. Time & Timezone Check</h2>';
echo '<pre>';
$now_local = new DateTime();
$now_utc = new DateTime('now', new DateTimeZone('UTC'));
echo 'Server Local Time: ' . $now_local->format('Y-m-d H:i:s T') . PHP_EOL;
echo 'Server UTC Time: ' . $now_utc->format('Y-m-d H:i:s T') . PHP_EOL;
echo 'WordPress Timezone: ' . get_option('timezone_string', 'Not set') . PHP_EOL;
echo 'WordPress GMT Offset: ' . get_option('gmt_offset', '0') . ' hours' . PHP_EOL;
echo '</pre>';

// 4. Check Plugin Version
echo '<h2>4. Plugin Information</h2>';
echo '<pre>';
if (is_plugin_active('events-cms-directory/events-cms-directory.php')) {
    $plugin_file = WP_PLUGIN_DIR . '/events-cms-directory/events-cms-directory.php';
    if (file_exists($plugin_file)) {
        $plugin_data = get_file_data($plugin_file, array('Version' => 'Version'));
        echo 'Plugin Status: <span class="success">✓ Active</span>' . PHP_EOL;
        echo 'Plugin Version: <span class="success">' . $plugin_data['Version'] . '</span>' . PHP_EOL;
        echo 'Expected Version: <span class="warning">1.1.4</span>' . PHP_EOL;
        
        if ($plugin_data['Version'] !== '1.1.4') {
            echo PHP_EOL . '<span class="error">⚠ VERSION MISMATCH!</span>' . PHP_EOL;
            echo 'The plugin file may not have been updated correctly.' . PHP_EOL;
            echo 'Try deactivating and reactivating the plugin.' . PHP_EOL;
        }
    } else {
        echo '<span class="error">❌ Plugin file not found</span>' . PHP_EOL;
    }
} else {
    echo 'Plugin Status: <span class="error">❌ Not Active</span>' . PHP_EOL;
}
echo '</pre>';

// 5. Test Date Filtering
echo '<h2>5. Client-Side Date Filter Test</h2>';
echo '<pre>';
if (isset($data) && is_array($data)) {
    $now = new DateTime('now', new DateTimeZone('UTC'));
    $filtered = array_filter($data, function($event) use ($now) {
        if (empty($event['start_at'])) return false;
        try {
            $event_date = new DateTime($event['start_at']);
            return $event_date >= $now;
        } catch (Exception $e) {
            return false;
        }
    });
    
    echo 'Events before filter: ' . count($data) . PHP_EOL;
    echo 'Events after filter: <span class="success">' . count($filtered) . '</span>' . PHP_EOL;
    echo 'Filtered out: <span class="warning">' . (count($data) - count($filtered)) . '</span> past events' . PHP_EOL;
    
    if (count($filtered) < count($data)) {
        echo PHP_EOL . '<span class="success">✓ Date filtering is working!</span>' . PHP_EOL;
    }
}
echo '</pre>';

echo '<hr>';
echo '<h2>✅ Next Steps</h2>';
echo '<pre>';
echo '1. Check the API URL setting above' . PHP_EOL;
echo '2. Verify plugin version matches expected (1.1.4)' . PHP_EOL;
echo '3. If version is wrong: Deactivate + Reactivate plugin' . PHP_EOL;
echo '4. Clear browser cache (Ctrl+Shift+Delete)' . PHP_EOL;
echo '5. <span class="error">DELETE THIS FILE</span> after reviewing!' . PHP_EOL;
echo '</pre>';

echo '<p><a href="/wp-admin/plugins.php" style="background: #0e639c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px;">Go to Plugins</a></p>';
echo '</body></html>';
?>
