'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { Calendar, LayoutDashboard, Plus, List, Globe, LogOut, RefreshCw, FileText, Users } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Add Events', href: '/add', icon: Plus },
  { name: 'Bulk Sync', href: '/sync', icon: RefreshCw },
  { name: 'Organizer Submissions', href: '/submissions', icon: FileText },
  { name: 'Organizers Management', href: '/organizers', icon: Users },
  { name: 'Manage Events', href: '/events', icon: List },
  { name: 'Public Directory', href: '/directory', icon: Globe },
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const [pendingCount, setPendingCount] = useState(0)

  useEffect(() => {
    fetchPendingCount()
    
    // Set up real-time subscription for changes
    const subscription = supabase
      .channel('submissions-changes')
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'event_submissions' },
        () => fetchPendingCount()
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  const fetchPendingCount = async () => {
    try {
      const { count, error } = await supabase
        .from('event_submissions')
        .select('*', { count: 'exact', head: true })
        .eq('status', 'pending')
      
      if (!error && count !== null) {
        setPendingCount(count)
      }
    } catch (error) {
      console.error('Failed to fetch pending count:', error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  return (
    <div className="flex h-full w-64 flex-col bg-gray-900 text-white">
      <div className="flex h-16 items-center gap-2 px-6 border-b border-gray-800">
        <Calendar className="h-8 w-8 text-blue-400" />
        <span className="text-xl font-bold">Event CMS</span>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          const isSubmissions = item.href === '/submissions'
          const showBadge = isSubmissions && pendingCount > 0
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors relative',
                isActive
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
              {showBadge && (
                <span className="ml-auto flex h-5 min-w-[20px] items-center justify-center rounded-full bg-red-600 px-1.5 text-xs font-bold text-white">
                  {pendingCount}
                </span>
              )}
            </Link>
          )
        })}
      </nav>
      <div className="border-t border-gray-800 p-4">
        <Button
          variant="ghost"
          className="w-full justify-start text-gray-400 hover:text-white hover:bg-gray-800"
          onClick={handleLogout}
        >
          <LogOut className="mr-3 h-5 w-5" />
          Logout
        </Button>
      </div>
    </div>
  )
}
