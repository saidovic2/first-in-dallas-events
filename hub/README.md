# First in Dallas - Event Organizer Hub

Organizer submission portal for hub.firstindallas.com

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up Supabase:**
   - Create account at [supabase.com](https://supabase.com)
   - Create new project
   - Run SQL from `HUB_SETUP_COMPLETE.md`
   - Copy your URL and anon key

3. **Configure environment:**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your Supabase credentials
   ```

4. **Run development server:**
   ```bash
   npm run dev
   ```

5. **Open:** http://localhost:3001

## Features

- 🔐 Supabase Authentication
- 📝 Multi-step Event Submission Wizard
- 📊 Organizer Dashboard
- 📋 My Submissions Page
- 🔄 CMS Integration
- ✅ Admin Approval Workflow

## Tech Stack

- Next.js 14
- TypeScript
- Tailwind CSS
- Supabase Auth
- React Hook Form
- Zod Validation

## Documentation

See `../HUB_SETUP_COMPLETE.md` for full setup instructions.
