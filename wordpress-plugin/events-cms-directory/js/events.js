/**
 * Events CMS Directory - Image Error Handling
 */

(function($) {
    'use strict';

    $(document).ready(function() {
        // Handle broken images in event cards
        $('.event-image img, .eventscms-widget-event-image img').on('error', function() {
            const $img = $(this);
            const $container = $img.parent();
            
            // Remove the broken image
            $img.remove();
            
            // Add placeholder class to container
            $container.addClass('event-image-placeholder');
            
            // Add calendar emoji as placeholder
            if (!$container.find('.placeholder-icon').length) {
                $container.append('<div class="placeholder-icon">📅</div>');
            }
        });

        // Check for images with empty or undefined src
        $('.event-image img, .eventscms-widget-event-image img').each(function() {
            const src = $(this).attr('src');
            if (!src || src === '' || src.includes('undefined') || src.includes('null')) {
                $(this).trigger('error');
            }
        });
    });

})(jQuery);
