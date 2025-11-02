<?php
/**
 * Plugin Name: Events CMS Directory
 * Plugin URI: https://github.com/saidovic2/events-cms-directory
 * Description: Display events from your Events CMS on WordPress pages using shortcodes and widgets
 * Version: 1.1.0
 * Author: Saidovic
 * Author URI: https://firstindallas.com
 * License: GPL2
 * GitHub Plugin URI: saidovic2/events-cms-directory
 * GitHub Branch: main
 * Requires at least: 5.0
 * Tested up to: 6.4
 * Requires PHP: 7.4
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

class EventsCMSDirectory {
    
    private $api_url;
    
    public function __construct() {
        // Get API URL from settings (default to localhost)
        $this->api_url = get_option('events_cms_api_url', 'http://localhost:8001/api');
        
        // Register shortcode
        add_shortcode('events_directory', array($this, 'display_events_directory'));
        
        // Add settings page
        add_action('admin_menu', array($this, 'add_settings_page'));
        add_action('admin_init', array($this, 'register_settings'));
        
        // Enqueue styles
        add_action('wp_enqueue_scripts', array($this, 'enqueue_styles'));
        
        // Register widget
        add_action('widgets_init', array($this, 'register_widgets'));
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
     * Register widgets
     */
    public function register_widgets() {
        register_widget('EventsCMS_Upcoming_Events_Widget');
    }
    
    /**
     * Display events directory shortcode
     */
    public function display_events_directory($atts) {
        // Parse shortcode attributes
        $atts = shortcode_atts(array(
            'status' => 'PUBLISHED',
            'show_filters' => 'yes',
        ), $atts);
        
        // Get filter values from URL
        $search = isset($_GET['search']) ? sanitize_text_field($_GET['search']) : '';
        $city = isset($_GET['city']) ? sanitize_text_field($_GET['city']) : '';
        $date = isset($_GET['date']) ? sanitize_text_field($_GET['date']) : '';
        $price_tier = isset($_GET['price_tier']) ? sanitize_text_field($_GET['price_tier']) : '';
        $current_page = isset($_GET['page_num']) ? max(1, intval($_GET['page_num'])) : 1;
        
        // Build params for API
        $params = array(
            'status' => $atts['status'],
            'search' => $search,
            'city' => $city,
            'price_tier' => $price_tier,
        );
        
        // Add date filter if specified
        if (!empty($date)) {
            $start_of_day = date('Y-m-d 00:00:00', strtotime($date));
            $end_of_day = date('Y-m-d 23:59:59', strtotime($date));
            $params['start_date'] = date('c', strtotime($start_of_day));
            $params['end_date'] = date('c', strtotime($end_of_day));
        }
        
        // Fetch all matching events from API
        $all_events = $this->fetch_events($params);
        
        if (is_wp_error($all_events)) {
            return '<p class="events-error">Unable to load events. Please try again later.</p>';
        }
        
        // Pagination
        $per_page = 20;
        $total_events = count($all_events);
        $total_pages = ceil($total_events / $per_page);
        $offset = ($current_page - 1) * $per_page;
        $events = array_slice($all_events, $offset, $per_page);
        
        // Get available cities for filter
        $cities = $this->get_cities();
        
        // Generate HTML output
        ob_start();
        
        // Show filters if enabled
        if ($atts['show_filters'] === 'yes') {
            echo $this->generate_filters_html($search, $city, $date, $price_tier, $cities);
        }
        
        if (empty($events)) {
            $message = !empty($date) ? 'No events found for this day. Try another date.' : 'No events found.';
            echo '<p class="events-empty">' . esc_html($message) . '</p>';
        } else {
            echo $this->generate_events_html($events);
            echo $this->generate_pagination_html($current_page, $total_pages, $total_events, $search, $city, $date, $price_tier);
        }
        
        return ob_get_clean();
    }
    
    /**
     * Fetch events from Events CMS API
     */
    private function fetch_events($params) {
        // Build query parameters
        $query_params = array(
            'limit' => 1000,
        );
        
        if (!empty($params['status'])) {
            $query_params['status'] = $params['status'];
        }
        
        if (!empty($params['city'])) {
            $query_params['city'] = $params['city'];
        }
        
        if (!empty($params['search'])) {
            $query_params['search'] = $params['search'];
        }
        
        if (!empty($params['price_tier'])) {
            $query_params['price_tier'] = $params['price_tier'];
        }
        
        if (!empty($params['start_date'])) {
            $query_params['start_date'] = $params['start_date'];
        }
        
        if (!empty($params['end_date'])) {
            $query_params['end_date'] = $params['end_date'];
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
        
        // API returns array directly
        if (is_array($data)) {
            return $data;
        }
        
        return array();
    }
    
    /**
     * Get list of cities from API
     */
    private function get_cities() {
        $url = $this->api_url . '/events/cities/list';
        
        $response = wp_remote_get($url, array(
            'timeout' => 10,
            'headers' => array(
                'Accept' => 'application/json',
            ),
        ));
        
        if (is_wp_error($response)) {
            return array();
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        return is_array($data) ? $data : array();
    }
    
    /**
     * Generate filters HTML
     */
    private function generate_filters_html($search, $city, $date, $price_tier, $cities) {
        // Get current URL without query params
        $base_url = strtok($_SERVER['REQUEST_URI'], '?');
        
        ob_start();
        ?>
        <div class="events-filters">
            <form method="get" action="<?php echo esc_url($base_url); ?>" class="events-filter-form">
                <div class="filter-row">
                    <div class="filter-group">
                        <label for="events-search">Search</label>
                        <input 
                            type="text" 
                            id="events-search" 
                            name="search" 
                            value="<?php echo esc_attr($search); ?>" 
                            placeholder="Search events..."
                            class="filter-input"
                        />
                    </div>
                    
                    <div class="filter-group">
                        <label for="events-city">City</label>
                        <select id="events-city" name="city" class="filter-select">
                            <option value="">All Cities</option>
                            <?php foreach ($cities as $city_option): ?>
                                <option value="<?php echo esc_attr($city_option); ?>" <?php selected($city, $city_option); ?>>
                                    <?php echo esc_html($city_option); ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="events-date">Date</label>
                        <input 
                            type="date" 
                            id="events-date" 
                            name="date" 
                            value="<?php echo esc_attr($date); ?>" 
                            class="filter-input"
                        />
                    </div>
                    
                    <div class="filter-group">
                        <label for="events-price">Price</label>
                        <select id="events-price" name="price_tier" class="filter-select">
                            <option value="">All Prices</option>
                            <option value="free" <?php selected($price_tier, 'free'); ?>>Free</option>
                            <option value="paid" <?php selected($price_tier, 'paid'); ?>>Paid</option>
                        </select>
                    </div>
                </div>
                
                <div class="filter-actions">
                    <button type="submit" class="filter-btn filter-btn-primary">Apply Filters</button>
                    <a href="<?php echo esc_url($base_url); ?>" class="filter-btn filter-btn-secondary">Clear</a>
                </div>
            </form>
        </div>
        <?php
        return ob_get_clean();
    }
    
    /**
     * Generate pagination HTML
     */
    private function generate_pagination_html($current_page, $total_pages, $total_events, $search, $city, $date, $price_tier) {
        if ($total_pages <= 1) {
            return '';
        }
        
        // Build query string
        $query_params = array();
        if (!empty($search)) $query_params['search'] = $search;
        if (!empty($city)) $query_params['city'] = $city;
        if (!empty($date)) $query_params['date'] = $date;
        if (!empty($price_tier)) $query_params['price_tier'] = $price_tier;
        
        $base_url = strtok($_SERVER['REQUEST_URI'], '?');
        
        ob_start();
        ?>
        <div class="events-pagination">
            <div class="pagination-info">
                Showing <?php echo (($current_page - 1) * 20) + 1; ?> to <?php echo min($current_page * 20, $total_events); ?> of <?php echo $total_events; ?> events
            </div>
            <div class="pagination-buttons">
                <?php if ($current_page > 1): ?>
                    <a href="<?php echo esc_url(add_query_arg(array_merge($query_params, array('page_num' => 1)), $base_url)); ?>" class="page-btn page-first" title="First page">&laquo;</a>
                    <a href="<?php echo esc_url(add_query_arg(array_merge($query_params, array('page_num' => $current_page - 1)), $base_url)); ?>" class="page-btn page-prev" title="Previous page">&lsaquo;</a>
                <?php else: ?>
                    <span class="page-btn page-disabled">&laquo;</span>
                    <span class="page-btn page-disabled">&lsaquo;</span>
                <?php endif; ?>
                
                <?php
                // Generate page numbers
                $pages_to_show = array();
                if ($total_pages <= 7) {
                    for ($i = 1; $i <= $total_pages; $i++) {
                        $pages_to_show[] = $i;
                    }
                } else {
                    if ($current_page <= 3) {
                        for ($i = 1; $i <= 4; $i++) $pages_to_show[] = $i;
                        $pages_to_show[] = '...';
                        $pages_to_show[] = $total_pages;
                    } elseif ($current_page >= $total_pages - 2) {
                        $pages_to_show[] = 1;
                        $pages_to_show[] = '...';
                        for ($i = $total_pages - 3; $i <= $total_pages; $i++) $pages_to_show[] = $i;
                    } else {
                        $pages_to_show[] = 1;
                        $pages_to_show[] = '...';
                        $pages_to_show[] = $current_page - 1;
                        $pages_to_show[] = $current_page;
                        $pages_to_show[] = $current_page + 1;
                        $pages_to_show[] = '...';
                        $pages_to_show[] = $total_pages;
                    }
                }
                
                foreach ($pages_to_show as $page):
                    if ($page === '...'):
                        ?><span class="page-ellipsis">...</span><?php
                    elseif ($page == $current_page):
                        ?><span class="page-btn page-current"><?php echo $page; ?></span><?php
                    else:
                        ?><a href="<?php echo esc_url(add_query_arg(array_merge($query_params, array('page_num' => $page)), $base_url)); ?>" class="page-btn"><?php echo $page; ?></a><?php
                    endif;
                endforeach;
                ?>
                
                <?php if ($current_page < $total_pages): ?>
                    <a href="<?php echo esc_url(add_query_arg(array_merge($query_params, array('page_num' => $current_page + 1)), $base_url)); ?>" class="page-btn page-next" title="Next page">&rsaquo;</a>
                    <a href="<?php echo esc_url(add_query_arg(array_merge($query_params, array('page_num' => $total_pages)), $base_url)); ?>" class="page-btn page-last" title="Last page">&raquo;</a>
                <?php else: ?>
                    <span class="page-btn page-disabled">&rsaquo;</span>
                    <span class="page-btn page-disabled">&raquo;</span>
                <?php endif; ?>
            </div>
        </div>
        <?php
        return ob_get_clean();
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

/**
 * Upcoming Events Widget
 */
class EventsCMS_Upcoming_Events_Widget extends WP_Widget {
    
    /**
     * Constructor
     */
    public function __construct() {
        parent::__construct(
            'eventscms_upcoming_events',
            'Upcoming Events',
            array('description' => 'Display upcoming events from Events CMS')
        );
    }
    
    /**
     * Front-end display of widget
     */
    public function widget($args, $instance) {
        $title = !empty($instance['title']) ? $instance['title'] : 'Events';
        $limit = !empty($instance['limit']) ? absint($instance['limit']) : 5;
        
        // Fetch upcoming events
        $events = $this->get_upcoming_events($limit);
        
        if (empty($events)) {
            return;
        }
        
        echo $args['before_widget'];
        
        if (!empty($title)) {
            echo $args['before_title'] . esc_html($title) . $args['after_title'];
        }
        
        echo '<div class="eventscms-widget-events">';
        
        foreach ($events as $event) {
            $event_date = new DateTime($event['start_at']);
            ?>
            <div class="eventscms-widget-event">
                <?php if (!empty($event['image_url'])): ?>
                    <div class="eventscms-widget-event-image">
                        <img src="<?php echo esc_url($event['image_url']); ?>" 
                             alt="<?php echo esc_attr($event['title']); ?>">
                    </div>
                <?php endif; ?>
                <div class="eventscms-widget-event-content">
                    <h4 class="eventscms-widget-event-title">
                        <?php if (!empty($event['source_url'])): ?>
                            <a href="<?php echo esc_url($event['source_url']); ?>" 
                               target="_blank" 
                               rel="noopener noreferrer">
                                <?php echo esc_html($event['title']); ?>
                            </a>
                        <?php else: ?>
                            <?php echo esc_html($event['title']); ?>
                        <?php endif; ?>
                    </h4>
                    <div class="eventscms-widget-event-date">
                        <?php echo esc_html($event_date->format('F j, Y')); ?>
                    </div>
                </div>
            </div>
            <?php
        }
        
        echo '</div>';
        
        // Add action buttons
        $calendar_url = !empty($instance['calendar_url']) ? $instance['calendar_url'] : '#';
        $submit_url = !empty($instance['submit_url']) ? $instance['submit_url'] : '#';
        ?>
        <div class="eventscms-widget-buttons">
            <a href="<?php echo esc_url($calendar_url); ?>" class="eventscms-widget-btn eventscms-btn-calendar">
                See events Calendar
            </a>
            <a href="<?php echo esc_url($submit_url); ?>" class="eventscms-widget-btn eventscms-btn-submit">
                Submit Your event
            </a>
        </div>
        <?php
        
        echo $args['after_widget'];
    }
    
    /**
     * Back-end widget form
     */
    public function form($instance) {
        $title = !empty($instance['title']) ? $instance['title'] : 'Events';
        $limit = !empty($instance['limit']) ? absint($instance['limit']) : 5;
        $calendar_url = !empty($instance['calendar_url']) ? $instance['calendar_url'] : '';
        $submit_url = !empty($instance['submit_url']) ? $instance['submit_url'] : '';
        ?>
        <p>
            <label for="<?php echo esc_attr($this->get_field_id('title')); ?>">
                Title:
            </label>
            <input class="widefat" 
                   id="<?php echo esc_attr($this->get_field_id('title')); ?>" 
                   name="<?php echo esc_attr($this->get_field_name('title')); ?>" 
                   type="text" 
                   value="<?php echo esc_attr($title); ?>">
        </p>
        <p>
            <label for="<?php echo esc_attr($this->get_field_id('limit')); ?>">
                Number of events to show:
            </label>
            <input class="tiny-text" 
                   id="<?php echo esc_attr($this->get_field_id('limit')); ?>" 
                   name="<?php echo esc_attr($this->get_field_name('limit')); ?>" 
                   type="number" 
                   step="1" 
                   min="1" 
                   max="10"
                   value="<?php echo esc_attr($limit); ?>" 
                   size="3">
        </p>
        <p>
            <label for="<?php echo esc_attr($this->get_field_id('calendar_url')); ?>">
                Calendar Page URL:
            </label>
            <input class="widefat" 
                   id="<?php echo esc_attr($this->get_field_id('calendar_url')); ?>" 
                   name="<?php echo esc_attr($this->get_field_name('calendar_url')); ?>" 
                   type="url" 
                   value="<?php echo esc_attr($calendar_url); ?>"
                   placeholder="https://yoursite.com/events-calendar">
        </p>
        <p>
            <label for="<?php echo esc_attr($this->get_field_id('submit_url')); ?>">
                Submit Event Page URL:
            </label>
            <input class="widefat" 
                   id="<?php echo esc_attr($this->get_field_id('submit_url')); ?>" 
                   name="<?php echo esc_attr($this->get_field_name('submit_url')); ?>" 
                   type="url" 
                   value="<?php echo esc_attr($submit_url); ?>"
                   placeholder="https://yoursite.com/submit-event">
        </p>
        <?php
    }
    
    /**
     * Update widget settings
     */
    public function update($new_instance, $old_instance) {
        $instance = array();
        $instance['title'] = (!empty($new_instance['title'])) ? sanitize_text_field($new_instance['title']) : '';
        $instance['limit'] = (!empty($new_instance['limit'])) ? absint($new_instance['limit']) : 5;
        $instance['calendar_url'] = (!empty($new_instance['calendar_url'])) ? esc_url_raw($new_instance['calendar_url']) : '';
        $instance['submit_url'] = (!empty($new_instance['submit_url'])) ? esc_url_raw($new_instance['submit_url']) : '';
        return $instance;
    }
    
    /**
     * Get upcoming events from API
     */
    private function get_upcoming_events($limit = 5) {
        $api_url = get_option('events_cms_api_url', 'http://localhost:8001/api');
        
        // Build URL with parameters
        $query_params = array(
            'status' => 'PUBLISHED',
            'limit' => $limit,
        );
        
        $url = add_query_arg($query_params, $api_url . '/events');
        
        // Make API request
        $response = wp_remote_get($url, array(
            'timeout' => 10,
            'headers' => array(
                'Accept' => 'application/json',
            ),
        ));
        
        if (is_wp_error($response)) {
            return array();
        }
        
        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);
        
        if (!is_array($data)) {
            return array();
        }
        
        // Filter only upcoming events (start_at >= now)
        $now = new DateTime();
        $upcoming = array_filter($data, function($event) use ($now) {
            if (empty($event['start_at'])) {
                return false;
            }
            $event_date = new DateTime($event['start_at']);
            return $event_date >= $now;
        });
        
        // Sort by date (earliest first)
        usort($upcoming, function($a, $b) {
            return strtotime($a['start_at']) - strtotime($b['start_at']);
        });
        
        return array_slice($upcoming, 0, $limit);
    }
}

// Initialize plugin
function events_cms_directory_init() {
    $plugin = new EventsCMSDirectory();
}
add_action('plugins_loaded', 'events_cms_directory_init');
