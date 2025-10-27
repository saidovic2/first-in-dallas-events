import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { createClient } from '@supabase/supabase-js'

export const supabase = createClientComponentClient()

// Server-side client
export const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export type Database = {
  public: {
    Tables: {
      organizers: {
        Row: {
          id: string
          email: string
          full_name: string | null
          organization_name: string | null
          phone: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          email: string
          full_name?: string | null
          organization_name?: string | null
          phone?: string | null
        }
        Update: {
          full_name?: string | null
          organization_name?: string | null
          phone?: string | null
        }
      }
      event_submissions: {
        Row: {
          id: string
          organizer_id: string
          title: string
          primary_url: string | null
          format: 'in-person' | 'online' | 'hybrid' | null
          country: string | null
          venue: string | null
          address: string | null
          city: string | null
          state: string | null
          zip_code: string | null
          start_date: string | null
          end_date: string | null
          price: number | null
          price_tier: 'free' | 'paid' | null
          image_url: string | null
          description: string | null
          organizer_contact: string | null
          submission_type: 'free' | 'paid'
          status: 'pending' | 'approved' | 'rejected' | 'published'
          admin_notes: string | null
          cms_event_id: number | null
          synced_to_cms: boolean
          published_to_wordpress: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          organizer_id: string
          title: string
          primary_url?: string | null
          format?: 'in-person' | 'online' | 'hybrid' | null
          country?: string | null
          venue?: string | null
          address?: string | null
          city?: string | null
          state?: string | null
          zip_code?: string | null
          start_date?: string | null
          end_date?: string | null
          price?: number | null
          price_tier?: 'free' | 'paid' | null
          image_url?: string | null
          description?: string | null
          organizer_contact?: string | null
          submission_type?: 'free' | 'paid'
        }
        Update: Partial<Omit<Database['public']['Tables']['event_submissions']['Insert'], 'organizer_id'>>
      }
    }
  }
}
