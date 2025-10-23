'use client'

import { useEffect, useState } from 'react'
import { User } from 'lucide-react'

export function Header() {
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
    }
  }, [])

  return (
    <header className="h-16 border-b bg-white px-6 flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          {/* Page title will be set by individual pages */}
        </h1>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100">
          <User className="h-5 w-5 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">
            {user?.name || 'Admin'}
          </span>
        </div>
      </div>
    </header>
  )
}
