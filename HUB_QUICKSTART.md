# 🚀 Event Organizer Hub - Quick Start Guide

Complete guide to setting up and running the organizer submission portal.

---

## ✅ What's Been Created

### Frontend (hub/ folder)
- ✅ Next.js 14 app with TypeScript
- ✅ Supabase authentication (signup/login)
- ✅ Dashboard with statistics
- ✅ 3-step submission wizard
- ✅ My Submissions page
- ✅ All UI components
- ✅ API integration layer

### Backend (api/routes/)
- ✅ submissions.py - New API endpoints for submissions

---

## 📋 Step-by-Step Setup

### Step 1: Create Supabase Project (5 minutes)

1. Go to [supabase.com](https://supabase.com) and sign up
2. Create new project
3. Go to **Settings** → **API** and copy:
   - Project URL
   - Anon/public key

### Step 2: Create Database Tables

In Supabase SQL Editor, run this:

```sql
-- Organizers table
CREATE TABLE organizers (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  email TEXT NOT NULL,
  full_name TEXT,
  organization_name TEXT,
  phone TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Event submissions table
CREATE TABLE event_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organizer_id UUID REFERENCES organizers(id) NOT NULL,
  
  title TEXT NOT NULL,
  primary_url TEXT,
  format TEXT CHECK (format IN ('in-person', 'online', 'hybrid')),
  country TEXT DEFAULT 'USA',
  
  venue TEXT,
  address TEXT,
  city TEXT,
  state TEXT,
  zip_code TEXT,
  start_date TIMESTAMP,
  end_date TIMESTAMP,
  price DECIMAL(10,2),
  price_tier TEXT CHECK (price_tier IN ('free', 'paid')),
  image_url TEXT,
  description TEXT,
  organizer_contact TEXT,
  
  submission_type TEXT CHECK (submission_type IN ('free', 'paid')) DEFAULT 'free',
  status TEXT CHECK (status IN ('pending', 'approved', 'rejected', 'published')) DEFAULT 'pending',
  admin_notes TEXT,
  
  cms_event_id INTEGER,
  synced_to_cms BOOLEAN DEFAULT FALSE,
  published_to_wordpress BOOLEAN DEFAULT FALSE,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE organizers ENABLE ROW LEVEL SECURITY;
ALTER TABLE event_submissions ENABLE ROW LEVEL SECURITY;

-- Organizers policies
CREATE POLICY "Users can view own profile"
  ON organizers FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON organizers FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
  ON organizers FOR INSERT WITH CHECK (auth.uid() = id);

-- Event submissions policies
CREATE POLICY "Users can view own submissions"
  ON event_submissions FOR SELECT USING (organizer_id = auth.uid());

CREATE POLICY "Users can create own submissions"
  ON event_submissions FOR INSERT WITH CHECK (organizer_id = auth.uid());

CREATE POLICY "Users can update own pending submissions"
  ON event_submissions FOR UPDATE
  USING (organizer_id = auth.uid() AND status = 'pending');
```

### Step 3: Configure Hub Environment

Create `hub/.env.local`:

```env
# From Supabase dashboard
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here

# Your CMS API
NEXT_PUBLIC_CMS_API_URL=http://localhost:8000/api

# App URLs
NEXT_PUBLIC_APP_URL=http://localhost:3001
NEXT_PUBLIC_MAIN_SITE_URL=http://localhost:3000
```

### Step 4: Add Backend API Routes

In `api/main.py`, add:

```python
from routes import submissions

# Add this line with your other router includes
app.include_router(submissions.router, prefix="/api/submissions", tags=["submissions"])
```

The file `api/routes/submissions.py` has already been created for you!

### Step 5: Run Everything

**Terminal 1 - CMS API:**
```powershell
cd api
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Main Web App:**
```powershell
cd web
npm run dev
```

**Terminal 3 - Hub (Organizer Portal):**
```powershell
cd hub
npm run dev
```

Now you have:
- CMS API: http://localhost:8000
- Main Site: http://localhost:3000
- Hub Portal: http://localhost:3001

---

## 🎯 Using the Hub

### For Organizers:

1. **Sign Up:** http://localhost:3001/auth/signup
   - Enter name, organization, email, password
   - Create account

2. **Dashboard:** http://localhost:3001/dashboard
   - View submission statistics
   - Quick actions

3. **Submit Event:** http://localhost:3001/submit
   - **Step 1:** Event title, URL, format, country
   - **Step 2:** Location, dates, price, description, image
   - **Step 3:** Choose Free or Paid (Featured)
   - Submit for review

4. **Track Status:** http://localhost:3001/submissions
   - See all your submissions
   - Track status (Pending/Published/Rejected)

### For Admins:

1. **View Submissions:** http://localhost:3000/events
   - Filter by Status: PENDING
   - See all organizer submissions

2. **Review & Approve:**
   - Click on pending event
   - Review details
   - Click "Publish" to approve
   - Or reject with reason

3. **Published Events:**
   - Approved events appear on main calendar
   - Sync to WordPress automatically

---

## 🔄 Workflow Diagram

```
Organizer                Hub Portal              CMS API              Main Site
   |                         |                       |                     |
   |-- Sign Up ------------->|                       |                     |
   |                         |                       |                     |
   |-- Submit Event -------->|                       |                     |
   |                         |-- POST /submissions ->|                     |
   |                         |                       |-- Create Event -----|
   |                         |                       |   (status=PENDING)  |
   |                         |<-- Success ----------|                     |
   |<-- Confirmation --------|                       |                     |
   |                         |                       |                     |
   |-- Check Status -------->|                       |                     |
   |                         |-- GET /submissions -->|                     |
   |<-- Status: Pending -----|<----------------------|                     |
   |                         |                       |                     |
   
Admin (CMS)                                     |                     |
   |                                            |                     |
   |-- View Pending -------------------------->|                     |
   |<-- Show Submissions ----------------------|                     |
   |                                            |                     |
   |-- Approve Submission -------------------->|                     |
   |                                            |-- Update Status --->|
   |                                            |   (PUBLISHED)       |
   |                                            |                     |
Organizer                                       |                     |
   |-- Check Status -------->|                 |                     |
   |<-- Status: Published ---|                 |                     |
                             |                 |                     |
Public                                         |<-- Event Appears ---|
   |-- View Calendar ---------------------------------------->| (Calendar)
```

---

## 📁 File Structure

```
hub/
├── app/
│   ├── auth/
│   │   ├── login/page.tsx         ✅ Login page
│   │   ├── signup/page.tsx        ✅ Signup page
│   │   └── callback/route.ts      ✅ Auth callback
│   ├── dashboard/page.tsx         ✅ Dashboard with stats
│   ├── submit/page.tsx            ✅ 3-step wizard
│   ├── submissions/page.tsx       ✅ My submissions
│   ├── layout.tsx                 ✅ Root layout
│   ├── page.tsx                   ✅ Redirect logic
│   └── globals.css                ✅ Styles
├── components/
│   ├── ui/                        ✅ All UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── label.tsx
│   │   ├── textarea.tsx
│   │   └── badge.tsx
│   └── layout/
│       └── nav.tsx                ✅ Navigation
├── lib/
│   ├── supabase.ts                ✅ Supabase client
│   ├── api.ts                     ✅ API integration
│   └── utils.ts                   ✅ Utilities
├── package.json                   ✅ Dependencies
├── tsconfig.json                  ✅ TypeScript config
└── .env.local                     ⚠️  YOU CREATE THIS

api/routes/
└── submissions.py                 ✅ Backend endpoints
```

---

## 🎨 Features Delivered

### Authentication
- ✅ Supabase Auth integration
- ✅ Signup with profile creation
- ✅ Login with session management
- ✅ Protected routes (dashboard, submit, submissions)
- ✅ Sign out functionality

### Dashboard
- ✅ Welcome message with user name
- ✅ Statistics cards (Total, Pending, Published, Rejected)
- ✅ Quick action cards (Submit Event, View Submissions)
- ✅ How It Works guide

### 3-Step Submission Wizard
- ✅ Progress bar with step indicators
- ✅ **Step 1:** Event title, URL, format, country
- ✅ **Step 2:** Location, dates, price, description, image, contact
- ✅ **Step 3:** Free vs Paid (Featured) selection
- ✅ Form validation
- ✅ Back/Next navigation
- ✅ Submit to Supabase + CMS API
- ✅ Success confirmation

### My Submissions
- ✅ List all submissions
- ✅ Color-coded status badges
- ✅ Status icons (clock, check, x)
- ✅ Submission details (date, location, format, type)
- ✅ Description preview
- ✅ Rejection reason display
- ✅ Empty state with CTA
- ✅ Success message after submission
- ✅ Info card about review process

### Backend API
- ✅ `POST /api/submissions` - Create submission
- ✅ `GET /api/submissions/by-organizer/{id}` - Get organizer's submissions
- ✅ `PATCH /api/submissions/{id}/approve` - Approve submission
- ✅ `PATCH /api/submissions/{id}/reject` - Reject with reason
- ✅ `GET /api/submissions/pending` - List pending for admins

---

## 🧪 Testing Checklist

### Organizer Flow
- [ ] Sign up new account
- [ ] Login with credentials
- [ ] View dashboard stats
- [ ] Navigate to Submit Event
- [ ] Complete Step 1 (Edit Event)
- [ ] Complete Step 2 (Review)
- [ ] Complete Step 3 (Promotion)
- [ ] Submit event
- [ ] See success message
- [ ] View event in My Submissions
- [ ] Check status is "Pending"

### Admin Flow
- [ ] Login to main CMS
- [ ] Go to Events page
- [ ] Filter by Status: PENDING
- [ ] See organizer submission
- [ ] Review details
- [ ] Approve event (status → PUBLISHED)
- [ ] Event appears on main calendar

### Organizer Check
- [ ] Refresh My Submissions
- [ ] Status updated to "Published"
- [ ] Event visible on public calendar

---

## 🔐 Security Features

- ✅ Row Level Security (RLS) in Supabase
- ✅ Users can only see/edit their own submissions
- ✅ Protected API routes (admin actions require auth)
- ✅ JWT token-based authentication
- ✅ Secure password hashing (Supabase)
- ✅ CORS configuration
- ✅ Input validation (client + server)

---

## 🚀 Deployment (Future)

### Hub Subdomain: hub.firstindallas.com

**Vercel Deployment:**
1. Push hub/ to GitHub
2. Connect to Vercel
3. Add environment variables
4. Deploy!

**Custom Subdomain:**
1. Add DNS record: `hub.firstindallas.com` → Vercel
2. Update Supabase redirect URLs
3. Update .env.local with production URLs

---

## 📧 Email Notifications (Phase 2)

To add email notifications:

1. Sign up for [Resend](https://resend.com) or SendGrid
2. Create email templates
3. Add to submission endpoint:
   - Send confirmation to organizer
   - Notify admin of new submission
4. Add to approve/reject endpoints:
   - Notify organizer of status change

---

## 💳 Payment Integration (Phase 2)

For paid/featured submissions:

1. Integrate Stripe checkout
2. Add payment flow before final submission
3. Store payment ID in submission
4. Auto-approve after successful payment
5. Manual billing for now as requested

---

## ✅ You're All Set!

Your Event Organizer Hub is ready to go! The complete system includes:

- Modern, professional UI
- Secure authentication
- Multi-step submission workflow
- Real-time status tracking
- Admin approval system
- CMS + WordPress integration

**Start here:** Create .env.local in hub/ folder with your Supabase credentials, then run the hub!

```powershell
cd hub
npm run dev
```

Visit: http://localhost:3001 🎉
