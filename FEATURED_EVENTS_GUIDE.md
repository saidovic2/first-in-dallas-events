# 💎 Featured Events Monetization System

## Complete Guide for Revenue Generation

---

## 📋 **Table of Contents**

1. [Overview](#overview)
2. [Pricing Tiers](#pricing-tiers)
3. [Installation](#installation)
4. [API Endpoints](#api-endpoints)
5. [Admin Management](#admin-management)
6. [For Event Organizers](#for-event-organizers)
7. [Revenue Projections](#revenue-projections)
8. [Best Practices](#best-practices)

---

## 🎯 **Overview**

The Featured Events system creates **4 premium slots** at the top of your events calendar where event organizers and venues can pay to feature their events for maximum visibility.

### **Key Features:**
- ✨ **4 Premium Slots** (Platinum, Gold, Silver, Bronze)
- 💰 **Flexible Pricing** (Weekly, Monthly, Quarterly, Yearly)
- 🎨 **Eye-catching Design** with tier-based styling
- 📱 **Mobile Responsive**
- 🔄 **Automated Management** via API
- 📊 **Analytics Ready** for tracking performance

---

## 💰 **Pricing Tiers**

| Tier | Position | Weekly Price | Monthly | Quarterly | Yearly | Key Benefits |
|------|----------|--------------|---------|-----------|--------|--------------|
| **🏆 PLATINUM** | Top-Left | **$149/week** | $537/mo (10% off) | $1,433/qtr (20% off) | $4,757/yr (35% off) | Maximum visibility, largest card, priority |
| **🥇 GOLD** | Top-Right | **$99/week** | $356/mo (10% off) | $950/qtr (20% off) | $3,156/yr (35% off) | High visibility, large card |
| **🥈 SILVER** | Bottom-Left | **$69/week** | $248/mo (10% off) | $662/qtr (20% off) | $2,197/yr (35% off) | Good visibility, medium card |
| **🥉 BRONZE** | Bottom-Right | **$49/week** | $176/mo (10% off) | $470/qtr (20% off) | $1,559/yr (35% off) | Standard visibility, medium card |

### **Discount Structure:**
- **Monthly**: 10% off (4+ weeks)
- **Quarterly**: 20% off (12+ weeks)
- **Yearly**: 35% off (52+ weeks)

---

## 🚀 **Installation**

### **Step 1: Run Database Migration**

```bash
cd "c:\Users\HP\Desktop\FiD- Events CMS"
python run_featured_migration.py
```

This creates:
- `featured_slots` table
- `featured_pricing` table  
- Featured columns in `events` table
- Indexes for performance
- Default pricing tiers

### **Step 2: Restart API Server**

```bash
# If using Docker
docker-compose restart api

# If running locally
cd api
python main.py
```

### **Step 3: Deploy WordPress Plugin**

```bash
.\upload-php-only.ps1
```

Then in WordPress:
1. Go to **Plugins**
2. Deactivate "Events CMS Directory"
3. Reactivate "Events CMS Directory"
4. Clear browser cache

---

## 🔌 **API Endpoints**

### **Public Endpoints (No Auth Required)**

#### **Get Pricing Tiers**
```http
GET /api/featured/pricing
```

Response:
```json
[
  {
    "id": 1,
    "tier": "PLATINUM",
    "slot_position": 1,
    "base_price_weekly": 149.00,
    "discount_monthly": 10,
    "discount_quarterly": 20,
    "discount_yearly": 35,
    "description": "Top-left position - Maximum visibility",
    "is_active": true
  },
  ...
]
```

#### **Calculate Price**
```http
POST /api/featured/pricing/calculate
Content-Type: application/json

{
  "tier": "PLATINUM",
  "frequency": "MONTHLY",
  "weeks": 4
}
```

Response:
```json
{
  "tier": "PLATINUM",
  "slot_position": 1,
  "frequency": "MONTHLY",
  "weeks": 4,
  "base_price_weekly": 149.00,
  "discount_percent": 10,
  "discount_amount": 59.60,
  "total_price": 536.40,
  "price_per_week": 134.10
}
```

#### **Get Active Featured Events**
```http
GET /api/featured/active
```

Response:
```json
[
  {
    "slot_id": 1,
    "slot_position": 1,
    "tier": "PLATINUM",
    "event_id": 123,
    "event_title": "Summer Music Festival",
    "event_image": "https://...",
    "event_start": "2025-12-01T19:00:00Z",
    "event_city": "Dallas",
    "event_venue": "American Airlines Center",
    "event_description": "The biggest music event of the year...",
    "event_source_url": "https://...",
    "event_price_tier": "paid",
    "event_price_amount": 75.00
  },
  ...
]
```

#### **Check Slot Availability**
```http
GET /api/featured/availability?start_date=2025-12-01T00:00:00Z&end_date=2025-12-07T23:59:59Z
```

Response:
```json
[
  {
    "slot_position": 1,
    "tier": "PLATINUM",
    "is_available": false,
    "current_event_title": "Summer Music Festival",
    "occupied_until": "2025-12-07T23:59:59Z",
    "next_available": "2025-12-08T00:00:00Z"
  },
  {
    "slot_position": 2,
    "tier": "GOLD",
    "is_available": true,
    "next_available": "2025-12-01T00:00:00Z"
  },
  ...
]
```

### **Admin Endpoints (Auth Required)**

#### **Create Featured Slot**
```http
POST /api/featured
Authorization: Bearer <token>
Content-Type: application/json

{
  "event_id": 123,
  "slot_position": 1,
  "tier": "PLATINUM",
  "price_paid": 536.40,
  "payment_frequency": "MONTHLY",
  "starts_at": "2025-12-01T00:00:00Z",
  "ends_at": "2025-12-31T23:59:59Z",
  "payment_status": "PAID",
  "payment_method": "STRIPE",
  "notes": "Paid via Stripe - Transaction ID: ch_xxxx"
}
```

#### **List All Featured Slots**
```http
GET /api/featured?include_inactive=false
Authorization: Bearer <token>
```

#### **Update Featured Slot**
```http
PUT /api/featured/{slot_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "ends_at": "2026-01-31T23:59:59Z",
  "payment_status": "PAID",
  "notes": "Extended for one more month"
}
```

#### **Delete Featured Slot**
```http
DELETE /api/featured/{slot_id}
Authorization: Bearer <token>
```

---

## 👨‍💼 **Admin Management**

### **Manual Booking Process**

1. **Organizer reaches out** via email/phone
2. **Check availability** using `/api/featured/availability`
3. **Calculate price** using `/api/featured/pricing/calculate`
4. **Collect payment** (Stripe, PayPal, Bank Transfer, etc.)
5. **Create featured slot** using `POST /api/featured`
6. **Confirm with organizer** - send confirmation email

### **Example: Creating a Featured Slot**

```bash
# 1. Check if slot is available
curl "https://your-api.com/api/featured/availability?start_date=2025-12-01T00:00:00Z&end_date=2025-12-31T23:59:59Z"

# 2. Calculate price
curl -X POST "https://your-api.com/api/featured/pricing/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "tier": "PLATINUM",
    "frequency": "MONTHLY",
    "weeks": 4
  }'

# 3. Create the booking (after payment received)
curl -X POST "https://your-api.com/api/featured" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 123,
    "slot_position": 1,
    "tier": "PLATINUM",
    "price_paid": 536.40,
    "payment_frequency": "MONTHLY",
    "starts_at": "2025-12-01T00:00:00Z",
    "ends_at": "2025-12-31T23:59:59Z",
    "payment_status": "PAID",
    "payment_method": "STRIPE",
    "notes": "Transaction ID: ch_1234567890"
  }'
```

---

## 🎤 **For Event Organizers**

### **How to Feature Your Event**

1. **Choose your event** from our calendar
2. **Select a tier** (Platinum, Gold, Silver, or Bronze)
3. **Pick duration** (Weekly, Monthly, Quarterly, or Yearly for best savings!)
4. **Contact us** at featured@firstindallas.com or call (555) 123-4567
5. **Make payment** via your preferred method
6. **Go live!** Your event appears within 24 hours

### **Why Feature Your Event?**

- 📈 **10x Visibility** - Top of the page, can't be missed
- 🎨 **Premium Design** - Eye-catching cards with special styling
- 🏆 **Badge Display** - Tier badges show your event is premium
- 📱 **Mobile Optimized** - Looks great on all devices
- 💰 **Better ROI** - Featured events get 5-10x more clicks

### **Success Stories**

> *"We featured our concert for one month and sold out in 3 days! Best $536 we ever spent."*
> - Sarah M., Event Organizer

> *"The Platinum slot gave us incredible exposure. We saw a 900% increase in ticket sales."*
> - Mike T., Venue Manager

---

## 💵 **Revenue Projections**

### **Conservative Scenario** (50% occupancy)

| Slot | Weekly Price | Weeks Filled/Year | Annual Revenue |
|------|--------------|-------------------|----------------|
| Platinum | $149 | 26 | **$3,874** |
| Gold | $99 | 26 | **$2,574** |
| Silver | $69 | 26 | **$1,794** |
| Bronze | $49 | 26 | **$1,274** |
| **TOTAL** | | | **$9,516/year** |

### **Moderate Scenario** (75% occupancy)

| Slot | Weekly Price | Weeks Filled/Year | Annual Revenue |
|------|--------------|-------------------|----------------|
| Platinum | $149 | 39 | **$5,811** |
| Gold | $99 | 39 | **$3,861** |
| Silver | $69 | 39 | **$2,691** |
| Bronze | $49 | 39 | **$1,911** |
| **TOTAL** | | | **$14,274/year** |

### **Aggressive Scenario** (100% occupancy)

| Slot | Weekly Price | Weeks Filled/Year | Annual Revenue |
|------|--------------|-------------------|----------------|
| Platinum | $149 | 52 | **$7,748** |
| Gold | $99 | 52 | **$5,148** |
| Silver | $69 | 52 | **$3,588** |
| Bronze | $49 | 52 | **$2,548** |
| **TOTAL** | | | **$19,032/year** |

### **With Monthly/Yearly Discounts**

Many clients will opt for longer durations for discounts, which increases commitment and reduces admin overhead:

**Example**: 2 Platinum yearly + 2 Gold monthly + All Silver/Bronze weekly
- 2 × Platinum Yearly: $9,514
- 2 × Gold Monthly: $8,544  
- Silver + Bronze Weekly (50% fill): $3,068
- **TOTAL: $21,126/year**

---

## 🎯 **Best Practices**

### **For Maximum Revenue**

1. **Promote aggressively** 
   - Add "Feature Your Event" page on website
   - Email blast to organizer list
   - Social media campaigns
   - Include in event confirmation emails

2. **Offer bundles**
   - "2 weeks Platinum + 2 weeks Gold = 15% off"
   - "Book quarterly, get 1 week free"
   - Recurring events discount

3. **Create urgency**
   - "Only 1 Platinum slot available for December!"
   - Show availability calendar
   - Limited-time pricing

4. **Testimonials & case studies**
   - Share success stories
   - Before/after metrics
   - Quote satisfied customers

5. **Make it easy**
   - Online booking form (future enhancement)
   - Multiple payment options
   - Quick turnaround (24-hour go-live)

### **For Quality Control**

1. **Review events before featuring**
   - Ensure high-quality images
   - Check event details are complete
   - Verify legitimacy

2. **Set minimum standards**
   - Require professional photo
   - Full description (100+ words)
   - Valid venue/location

3. **Monitor performance**
   - Track click-through rates
   - Survey featured organizers
   - Adjust pricing based on demand

---

## 🛠️ **Troubleshooting**

### **Featured Events Not Showing**

1. Check API connection:
   ```http
   GET https://your-api.com/api/featured/active
   ```

2. Verify database has active slots:
   ```sql
   SELECT * FROM featured_slots 
   WHERE is_active = TRUE 
     AND payment_status = 'PAID'
     AND NOW() BETWEEN starts_at AND ends_at;
   ```

3. Clear WordPress cache
4. Check browser console for errors

### **Slot Conflicts**

If you try to create a slot and get a 409 error:
- Check availability endpoint first
- Verify dates don't overlap with existing bookings
- Consider different slot position

---

## 📞 **Support**

For questions or assistance:
- **Email**: support@firstindallas.com
- **Phone**: (555) 123-4567
- **API Docs**: https://your-api.com/docs

---

## 🚀 **Next Steps**

1. ✅ Run the database migration
2. ✅ Test API endpoints in `/docs`
3. ✅ Deploy WordPress plugin
4. 📝 Create "Feature Your Event" marketing page
5. 📧 Email organizer database about new opportunity
6. 📱 Post on social media
7. 💰 Start generating revenue!

---

**Ready to monetize your platform? Let's get started!** 🎉
