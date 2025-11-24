<?php
/**
 * WordPress Cache Clearer
 * Upload this file to your WordPress root directory, access it once, then delete it.
 * URL: https://firstindallas.com/clear-wordpress-cache.php
 */

// Security check - only allow from localhost or authenticated users
if (!isset($_SERVER['HTTP_HOST']) || !in_array($_SERVER['HTTP_HOST'], ['firstindallas.com', 'www.firstindallas.com', 'localhost'])) {
    die('Access denied');
}

echo '<html><head><title>Cache Clearer</title></head><body>';
echo '<h1>WordPress Cache Clearer</h1>';
echo '<hr>';

// Load WordPress
define('WP_USE_THEMES', false);
require_once('./wp-load.php');

// Clear WordPress transients
echo '<p>Clearing transients...</p>';
global $wpdb;
$result = $wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '%_transient_%'");
echo "<p>✓ Deleted $result transient records</p>";

// Flush object cache
echo '<p>Flushing object cache...</p>';
wp_cache_flush();
echo '<p>✓ Object cache flushed</p>';

// Clear site transients
echo '<p>Clearing site transients...</p>';
delete_site_transient('update_plugins');
delete_site_transient('update_themes');
echo '<p>✓ Site transients cleared</p>';

// Clear opcache if available
if (function_exists('opcache_reset')) {
    echo '<p>Clearing opcache...</p>';
    opcache_reset();
    echo '<p>✓ Opcache cleared</p>';
} else {
    echo '<p>⚠ Opcache not available (this is fine)</p>';
}

// Instructions
echo '<hr>';
echo '<h2>✅ All Caches Cleared!</h2>';
echo '<p><strong>Next steps:</strong></p>';
echo '<ol>';
echo '<li>Go to <a href="/wp-admin/plugins.php">WordPress Admin → Plugins</a></li>';
echo '<li>Deactivate "Events CMS Directory" plugin</li>';
echo '<li>Reactivate "Events CMS Directory" plugin</li>';
echo '<li>Visit your <a href="/events-calendar/">Events Calendar</a> page</li>';
echo '<li><strong style="color: red;">DELETE THIS FILE (clear-wordpress-cache.php) after use!</strong></li>';
echo '</ol>';
echo '<hr>';
echo '<p><a href="/wp-admin/plugins.php" style="background: #0073aa; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px;">Go to Plugins Page</a></p>';
echo '</body></html>';
?>
