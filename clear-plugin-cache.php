<?php
/**
 * Clear WordPress Plugin Cache
 * Upload this to your WordPress root, visit it once, then delete it
 */

// Clear all plugin cache
delete_site_transient('update_plugins');
wp_cache_flush();

// Clear specific plugin transients
global $wpdb;
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '%_site_transient_%' OR option_name LIKE '%_transient_%'");

// Clear opcache if available
if (function_exists('opcache_reset')) {
    opcache_reset();
}

echo "<h1>✅ WordPress Cache Cleared!</h1>";
echo "<p>All plugin caches, transients, and opcache have been cleared.</p>";
echo "<p><strong>Now go back to WordPress and refresh the Plugins page.</strong></p>";
echo "<p><a href='/wp-admin/plugins.php'>Go to Plugins</a></p>";
echo "<hr>";
echo "<p style='color: red;'><strong>IMPORTANT: Delete this file after use!</strong></p>";
?>
