<?php
/**
 * Plugin Name: Events CMS Directory
 * Plugin URI: https://github.com/yourusername/events-cms
 * Description: Display events from your Events CMS on WordPress pages using shortcodes
 * Version: 1.0.0
 * Author: Your Name
 * Author URI: https://yourwebsite.com
 * License: GPL2
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class EventsCMSDirectory {
    
    private $api_url;
    
    public function __init() {
        // Get API URL from settings (default to localhost)
        $this->api_url = get_option('events_cms_api_url', 'http://localhost:8001/api');
        
        // Register shortcode
        add_shortcode('events_directory', array($this, 'display_events_directory'));
        
        // Add settings page
        add_action('admin_menu', array($this, 'add_settings_page'));
        add_action('admin_init', array($this, 'register_settings'));
        
        // Enqueue styles
        add_action('wp_enqueue_scripts', array($this, 'enqueue_styles'));
    }
    
    /**
     * Register plugin settings
     */
    public function register_settings() {
        register_setting('events_cms_settings', 'events_cms_api_url');
    }
    
    /**
     * Add settings page to WordPress admin
     */
    public function add_settings_page() {
        add_options_page(
            'Events CMS Settings',
            'Events CMS',
            'manage_options',
            'events-cms-settings',
            array($this, 'settings_page_html')
        );
    }
    
    /**
     * Settings page HTML
     */
    public function settings_page_html() {
        if (!current_user_can('manage_options')) {
            return;
        }
        ?>
        <div class="wrap">
            <h1><?php echo esc_html(get_admin_page_title()); ?></h1>
            <form action="options.php" method="post">
                <?php
                settings_fields('events_cms_settings');
                do_settings_sections('events_cms_settings');
                ?>
                <table class="form-table">
                    <tr>
                        <th scope="row">
                            <label for="events_cms_api_url">Events CMS API URL</label>
                        </th>
                        <td>
                            <input type="url" 
                                   id="events_cms_api_url" 
                                   name="events_cms_api_url" 
                                   value="<?php echo esc_attr(get_option('events_cms_api_url', 'http://localhost:8001/api')); ?>" 
                                   class="regular-text"
                                   placeholder="http://localhost:8001/api">
                            <p class="description">
                                The base URL of your Events CMS API (e.g., http://localhost:8001/api or https://api.yoursite.com/api)
                            </p>
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
            
            <hr>
            
            <h2>How to Use</h2>
            <p>Add the events directory to any page using this shortcode:</p>
            <code>[events_directory]</code>
            
            <h3>Shortcode Parameters:</h3>
            <ul>
                <li><code>[events_directory limit="10"]</code> - Show only 10 events</li>
                <li><code>[events_directory city="Dallas"]</code> - Filter by city</li>
                <li><code>[events_directory category="Music"]</code> - Filter by category</li>
                <li><code>[events_directory status="PUBLISHED"]</code> - Show only published events</li>
            </ul>
            
            <h3>Example:</h3>
            <code>[events_directory city="Dallas" limit="20" category="Music"]</code>
        </div>
        <?php
    }
    
    /**
     * Enqueue plugin styles
     */
    public function enqueue_styles() {
        wp_enqueue_style(
            'events-cms-directory',
            plugin_dir_url(__FILE__) . 'css/style.css',
            array(),
            '1.0.0'
        );
    }
    
    /**
     * Display events directory shortcode
     */
    public function display_events_directory($atts) {
        // Parse shortcode attributes
        $atts = shortcode_atts(array(
            'limit' => 20,
            'city' => '',
            'category' => '',
            'status' => 'PUBLISHED',
            'source_type' => '',
        ), $atts);
        
        // Fetch events from API
        $events = $this->fetch_events($atts);
        
        if (is_wp_error($events)) {
            return '<p class="events-error">Unable to load events. Please try again later.</p>';
        }
        
        if (empty($events)) {
            return '<p class="events-empty">No events found.</p>';
        }
        
        // Generate HTML output
        return $this->generate_events_html($events);
    }
    
    /**
     * Fetch events from Events CMS API
     */
    private function fetch_events($params) {
        // Build query parameters
        $query_params = array(
            'limit' => $params['limit'],
            'skip' => 0,
        );
        
        if (!empty($params['city'])) {
            $query_params['city'] = $params['city'];
        }
        
        if (!empty($params['category'])) {
            $query_params['category'] = $params['category'];
        }
        
        if (!empty($params['status'])) {
            $query_params['status'] = $params['status'];
        }
        
        if (!empty($params['source_type'])) {
            $query_params['source_type'] = $params['source_type'];
        }
        
        $url = add_query_arg($query_params, $this->api_url . '/events');
        
        // Make API request
        $response = wp_remote_get($url, array(
            'timeout' => 15,
            'headers' => array(
                'Accept' => 'application/json',
            ),
        ));
        
        if (is_wp_error($response)) {
            return $response;
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        // API returns array directly, not wrapped in "events" key
        if (is_array($data) && !isset($data['events'])) {
            return $data;
        }
        
        return isset($data['events']) ? $data['events'] : array();
    }
    
    /**
     * Generate HTML for events list
     */
    private function generate_events_html($events) {
        ob_start();
        ?>
        <div class="events-cms-directory">
            <div class="events-grid">
                <?php foreach ($events as $event): ?>
                    <div class="event-card">
                        <?php if (!empty($event['image_url'])): ?>
                            <div class="event-image">
                                <img src="<?php echo esc_url($event['image_url']); ?>" 
                                     alt="<?php echo esc_attr($event['title']); ?>">
                            </div>
                        <?php endif; ?>
                        
                        <div class="event-content">
                            <h3 class="event-title"><?php echo esc_html($event['title']); ?></h3>
                            
                            <div class="event-meta">
                                <div class="event-date">
                                    <svg class="icon" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"></path>
                                    </svg>
                                    <?php 
                                    $date = new DateTime($event['start_at']);
                                    echo esc_html($date->format('F j, Y'));
                                    ?>
                                </div>
                                
                                <?php if (!empty($event['venue'])): ?>
                                    <div class="event-venue">
                                        <svg class="icon" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"></path>
                                        </svg>
                                        <?php echo esc_html($event['venue']); ?>
                                    </div>
                                <?php endif; ?>
                                
                                <?php if (!empty($event['city'])): ?>
                                    <div class="event-city">
                                        <?php echo esc_html($event['city']); ?>
                                    </div>
                                <?php endif; ?>
                                
                                <?php if (!empty($event['category'])): ?>
                                    <div class="event-category">
                                        <span class="category-badge"><?php echo esc_html($event['category']); ?></span>
                                    </div>
                                <?php endif; ?>
                            </div>
                            
                            <?php if (!empty($event['description'])): ?>
                                <div class="event-description">
                                    <?php echo wp_kses_post(wp_trim_words($event['description'], 30)); ?>
                                </div>
                            <?php endif; ?>
                            
                            <div class="event-footer">
                                <div class="event-price">
                                    <?php 
                                    if ($event['price_tier'] === 'FREE') {
                                        echo '<span class="price-free">FREE</span>';
                                    } else {
                                        echo '<span class="price-paid">PAID</span>';
                                        if (!empty($event['price_amount'])) {
                                            echo ' <span class="price-amount">$' . number_format($event['price_amount'], 2) . '</span>';
                                        }
                                    }
                                    ?>
                                </div>
                                
                                <?php if (!empty($event['source_url'])): ?>
                                    <a href="<?php echo esc_url($event['source_url']); ?>" 
                                       class="event-link" 
                                       target="_blank" 
                                       rel="noopener noreferrer">
                                        View Details →
                                    </a>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
}

// Initialize plugin
function events_cms_directory_init() {
    $plugin = new EventsCMSDirectory();
    $plugin->__init();
}
add_action('plugins_loaded', 'events_cms_directory_init');
