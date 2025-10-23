# 🎯 Feature Documentation

Complete guide to all features in Local Event CMS.

---

## 🔐 Authentication System

### Login
- **Route**: `/login`
- **Features**:
  - Email/password authentication
  - JWT token-based sessions
  - Secure password hashing (bcrypt)
  - Remember me functionality
  - Error handling with user-friendly messages

### Default Credentials
```
Email: admin@example.com
Password: admin123
```

### Security
- JWT tokens with 7-day expiration
- Automatic token refresh
- Protected routes with middleware
- Password hashing with bcrypt
- CORS configuration

---

## 📊 Dashboard

### Route
`/dashboard`

### Statistics Cards

#### 1. Events This Week
- Count of events created in the last 7 days
- Shows total events count
- Real-time updates

#### 2. Total Extractions
- Number of URL extraction tasks
- Success rate percentage
- Performance indicator

#### 3. Active Sources
- Count of monitored event sources
- Status tracking
- Health monitoring

#### 4. Failed Tasks
- Count of failed extraction attempts
- Requires attention indicator
- Error tracking

### Charts & Analytics

#### Events by Status
- Draft vs Published breakdown
- Visual status indicators
- Real-time counts

#### Top Cities
- Top 10 cities by event count
- Sorted by popularity
- Geographic insights

#### Top Sources
- Most productive event sources
- Event count per source
- Source performance tracking

#### Recent Errors
- Last 5 failed extraction tasks
- Error messages
- Timestamps
- URLs that failed

---

## ➕ Add Events

### Route
`/add`

### URL Input
- **Multi-URL Support**: Add multiple URLs at once
- **Dynamic Fields**: Add/remove URL fields
- **Auto-Detection**: Automatically detects source type
- **Validation**: URL format validation

### Supported Sources

#### 1. JSON-LD (Schema.org)
```javascript
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "Event Title",
  "startDate": "2024-06-15T19:00",
  "location": {...}
}
```

#### 2. ICS/iCal Files
- Calendar file format (.ics)
- Supports VEVENT components
- Extracts dates, locations, descriptions

#### 3. RSS/Atom Feeds
- News feeds with event posts
- Extracts from feed items
- Supports media attachments

#### 4. Facebook Events
- Public Facebook event pages
- Extracts event details
- Requires public access

#### 5. Instagram Posts
- Instagram posts with event info
- Extracts from captions
- Image extraction

#### 6. Generic Webpages
- Fallback extraction method
- Uses Open Graph tags
- Meta tag parsing
- Heuristic date detection

### Extraction Process

1. **Queue Task**: URL added to Redis queue
2. **Worker Processing**: Background worker picks up task
3. **Detection**: Identifies source type
4. **Extraction**: Runs appropriate extractor
5. **Normalization**: Converts to standard format
6. **Deduplication**: Checks for existing events (fid_hash)
7. **Storage**: Saves to database
8. **Status Update**: Updates task status

### Task Status
- **Queued**: Waiting for processing
- **Running**: Currently being processed
- **Done**: Successfully extracted
- **Failed**: Extraction failed (with error message)

---

## 📝 Manage Events

### Route
`/events`

### Event List View

#### Display Options
- **Card View**: Rich event cards with images
- **Compact View**: Table-like listing
- **Responsive**: Adapts to screen size

#### Event Card Information
- Event title
- Date and time (formatted)
- Venue and location
- City
- Category badge
- Status badge (draft/published)
- Source type badge
- Price tier
- Description (truncated)
- Event image (if available)

### Filtering

#### Status Filter
- All events
- Draft only
- Published only

#### Search
- Search by title
- Search by description
- Search by venue
- Real-time search

#### Advanced Filters (Coming Soon)
- Date range
- City
- Category
- Price tier

### Actions

#### Edit Event
- Inline editing
- Update title, description
- Change dates
- Modify location
- Update category
- Change price information

#### Publish/Unpublish
- Toggle event status
- Draft → Published
- Published → Draft
- Affects public directory visibility

#### Push to WordPress
- One-click publishing
- Requires WP configuration
- Creates new post
- Stores WP post ID
- Includes event metadata

#### Delete Event
- Confirmation dialog
- Permanent deletion
- Removes from database

#### View Original
- Opens source URL in new tab
- Verify original event details
- Cross-reference information

---

## 🌐 Public Directory

### Route
`/directory`

### Public Features
- **No Authentication Required**: Accessible to everyone
- **SEO Friendly**: Optimized for search engines
- **Responsive Design**: Mobile, tablet, desktop

### Filtering System

#### Search
- Full-text search
- Searches title, description, venue
- Real-time results

#### City Filter
- Dropdown with all cities
- Populated from events
- "All Cities" option

#### Category Filter
- Dropdown with all categories
- Populated from events
- "All Categories" option

#### Price Filter
- Free events only
- Paid events only
- All prices

### View Modes

#### Grid View
- 3-column layout (desktop)
- 2-column layout (tablet)
- 1-column layout (mobile)
- Event cards with images
- Hover effects
- Quick info display

#### List View
- Full-width rows
- Larger images
- More description text
- Detailed information
- Better for scanning

### Event Cards

#### Information Displayed
- Event title
- Featured image
- Start date/time
- End date/time (if available)
- Venue name
- City
- Price tier badge
- Category badge
- Description preview
- "View Details" button

#### Card Actions
- Click to view original source
- Opens in new tab
- Preserves user context

---

## 🔄 WordPress Integration

### Configuration

#### Environment Variables
```env
WP_BASE_URL=https://your-wordpress-site.com
WP_USER=your-username
WP_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

#### WordPress Setup
1. WordPress 4.7+ (REST API included)
2. Create Application Password:
   - Users → Profile
   - Application Passwords section
   - Generate new password
3. Add credentials to `.env`
4. Restart API service

### Publishing Process

1. **Select Event**: From Manage Events page
2. **Click "Push to WordPress"**: Initiates publishing
3. **API Call**: Sends event data to WP REST API
4. **Post Creation**: Creates new WordPress post
5. **Metadata**: Includes event details as meta fields
6. **ID Storage**: Saves WP post ID in database
7. **Confirmation**: Shows success message

### Published Post Structure

#### Title
Event title

#### Content
- Event details section
- Date and time
- Venue and address
- City
- Price information
- Link to original source
- Event description

#### Metadata
- `event_start`: ISO datetime
- `event_venue`: Venue name
- `event_city`: City name

---

## 📈 Analytics & Statistics

### Dashboard Metrics

#### Event Metrics
- Total events count
- Events this week
- Events by status (draft/published)
- Events by city (top 10)
- Events by category

#### Extraction Metrics
- Total extraction tasks
- Success rate percentage
- Failed tasks count
- Average processing time

#### Source Metrics
- Active sources count
- Top performing sources
- Events per source
- Source reliability

#### Error Tracking
- Recent errors (last 5)
- Error messages
- Failed URLs
- Timestamps

---

## 🎨 UI/UX Features

### Design System

#### Colors
- Primary: Blue (#3B82F6)
- Secondary: Gray
- Success: Green
- Warning: Yellow
- Error: Red
- Neutral: Gray scale

#### Typography
- Font: Inter (Google Fonts)
- Headings: Bold, larger sizes
- Body: Regular, readable sizes
- Code: Monospace font

#### Components
- **Cards**: Elevated, rounded corners
- **Buttons**: Primary, secondary, outline variants
- **Badges**: Status indicators, categories
- **Inputs**: Clean, accessible forms
- **Icons**: Lucide React icons

### Responsive Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Accessibility
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus indicators
- Color contrast (WCAG AA)

---

## 🔧 Advanced Features

### Deduplication
- MD5 hash generation (fid_hash)
- Based on: title + start_date + source_url
- Prevents duplicate events
- Automatic checking

### Error Handling
- User-friendly error messages
- Detailed error logging
- Retry mechanisms
- Graceful degradation

### Performance
- Lazy loading images
- Pagination support
- Database indexing
- Redis caching
- Optimized queries

### Security
- JWT authentication
- Password hashing
- SQL injection prevention
- XSS protection
- CORS configuration
- Environment variables

---

## 🚀 Future Enhancements

### Planned Features
- [ ] Recurring events support
- [ ] Email notifications
- [ ] Calendar export (ICS)
- [ ] Social media sharing
- [ ] Event reminders
- [ ] User roles and permissions
- [ ] Bulk operations
- [ ] Advanced analytics
- [ ] API webhooks
- [ ] Multi-language support

### Integration Opportunities
- [ ] Google Calendar sync
- [ ] Eventbrite integration
- [ ] Meetup.com integration
- [ ] Stripe payment processing
- [ ] SendGrid email service
- [ ] Twilio SMS notifications

---

## 📱 Mobile Experience

### Responsive Features
- Touch-friendly buttons
- Swipe gestures
- Mobile-optimized forms
- Adaptive layouts
- Fast loading
- Offline support (planned)

### Mobile Navigation
- Hamburger menu
- Bottom navigation
- Swipe to navigate
- Pull to refresh

---

## 🎯 Use Cases

### Event Organizers
- Aggregate events from multiple sources
- Centralized event management
- Publish to multiple platforms
- Track event performance

### Community Managers
- Curate local events
- Promote community activities
- Share event calendars
- Build event directories

### Media & Publishers
- Automated event listings
- Content aggregation
- Event journalism
- Community engagement

### Venues
- Showcase upcoming events
- Manage event calendar
- Promote venue activities
- Track attendance

---

**All features are production-ready and fully documented!** 🎉
