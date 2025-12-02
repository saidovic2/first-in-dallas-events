'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function BulkSyncPage() {
  const router = useRouter()
  const [loading, setLoading] = useState<{eventbrite: boolean, ticketmaster: boolean, dallasArboretum: boolean, klydeWarrenPark: boolean}>({
    eventbrite: false,
    ticketmaster: false,
    dallasArboretum: false,
    klydeWarrenPark: false
  })
  const [status, setStatus] = useState<any>(null)
  const [message, setMessage] = useState<{type: 'success' | 'error' | 'info', text: string} | null>(null)
  const [activeTask, setActiveTask] = useState<any>(null)
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null)

  useEffect(() => {
    fetchSyncStatus()
    // Refresh status every 10 seconds
    const interval = setInterval(fetchSyncStatus, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchSyncStatus = async () => {
    try {
      const token = localStorage.getItem('token')
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/api/sync/status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setStatus(data)
      }
    } catch (error) {
      console.error('Error fetching sync status:', error)
    }
  }

  const pollTaskStatus = async (taskId: number) => {
    const token = localStorage.getItem('token')
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
    const response = await fetch(`${apiUrl}/api/tasks/${taskId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const task = await response.json()
      setActiveTask(task)
      
      if (task.status === 'completed' || task.status === 'failed') {
        if (pollingInterval) {
          clearInterval(pollingInterval)
          setPollingInterval(null)
        }
        setLoading(prev => ({ ...prev, eventbrite: false }))
        
        if (task.status === 'completed') {
          setMessage({
            type: 'success',
            text: `🎉 Sync completed successfully! Imported ${task.events_extracted || 0} new events. Refresh the events page to see them.`
          })
        } else {
          setMessage({
            type: 'error',
            text: `❌ Sync failed: ${task.error_message || 'Unknown error'}`
          })
        }
        
        setTimeout(() => setActiveTask(null), 15000)  // Keep visible for 15 seconds after completion
        fetchSyncStatus()
      }
    }
  }

  const syncEventbriteEvents = async () => {
    setLoading(prev => ({ ...prev, eventbrite: true }))
    setMessage(null)
    setActiveTask(null)
    
    try {
      const token = localStorage.getItem('token')
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/api/sync/eventbrite/dallas`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setMessage({
          type: 'info',
          text: `🔄 Sync started! Processing 20 organizers...`
        })
        
        // Start polling for task status (every 3 seconds)
        if (data.task_id) {
          const interval = setInterval(() => pollTaskStatus(data.task_id), 3000)
          setPollingInterval(interval)
        }
        
        setTimeout(fetchSyncStatus, 2000)
      } else {
        throw new Error('Failed to start sync')
      }
    } catch (error: any) {
      const errorMsg = error?.message || 'Unknown error'
      setMessage({
        type: 'error',
        text: `❌ Error starting Eventbrite sync: ${errorMsg}. Check that your API token is set.`
      })
      setLoading(prev => ({ ...prev, eventbrite: false }))
    }
  }

  const syncTicketmasterEvents = async () => {
    setLoading(prev => ({ ...prev, ticketmaster: true }))
    setMessage(null)
    setActiveTask(null)
    
    try {
      const token = localStorage.getItem('token')
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/api/sync/ticketmaster/dallas`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setMessage({
          type: 'info',
          text: `🔄 Ticketmaster sync started! Fetching events from Dallas-Fort Worth area...`
        })
        
        // Start polling for task status (every 3 seconds)
        if (data.task_id) {
          const interval = setInterval(() => pollTaskStatus(data.task_id), 3000)
          setPollingInterval(interval)
        }
        
        setTimeout(fetchSyncStatus, 2000)
      } else {
        throw new Error('Failed to start sync')
      }
    } catch (error: any) {
      const errorMsg = error?.message || 'Unknown error'
      setMessage({
        type: 'error',
        text: `❌ Error starting Ticketmaster sync: ${errorMsg}. Check that your API key is set.`
      })
      setLoading(prev => ({ ...prev, ticketmaster: false }))
    }
  }

  const syncDallasArboretumEvents = async () => {
    setLoading(prev => ({ ...prev, dallasArboretum: true }))
    setMessage(null)
    setActiveTask(null)
    
    try {
      const token = localStorage.getItem('token')
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/api/sync/dallas-arboretum`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setMessage({
          type: 'info',
          text: `🔄 Dallas Arboretum sync started! Fetching family-friendly events...`
        })
        
        // Start polling for task status (every 3 seconds)
        if (data.task_id) {
          const interval = setInterval(() => pollTaskStatus(data.task_id), 3000)
          setPollingInterval(interval)
        }
        
        setTimeout(fetchSyncStatus, 2000)
      } else {
        throw new Error('Failed to start sync')
      }
    } catch (error: any) {
      const errorMsg = error?.message || 'Unknown error'
      setMessage({
        type: 'error',
        text: `❌ Error starting Dallas Arboretum sync: ${errorMsg}.`
      })
      setLoading(prev => ({ ...prev, dallasArboretum: false }))
    }
  }

  const syncKlydeWarrenParkEvents = async () => {
    setLoading(prev => ({ ...prev, klydeWarrenPark: true }))
    setMessage(null)
    setActiveTask(null)
    
    try {
      const token = localStorage.getItem('token')
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/api/sync/klyde-warren-park`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setMessage({
          type: 'info',
          text: `🔄 Klyde Warren Park sync started! Fetching community events...`
        })
        
        // Start polling for task status (every 3 seconds)
        if (data.task_id) {
          const interval = setInterval(() => pollTaskStatus(data.task_id), 3000)
          setPollingInterval(interval)
        }
        
        setTimeout(fetchSyncStatus, 2000)
      } else {
        throw new Error('Failed to start sync')
      }
    } catch (error: any) {
      const errorMsg = error?.message || 'Unknown error'
      setMessage({
        type: 'error',
        text: `❌ Error starting Klyde Warren Park sync: ${errorMsg}.`
      })
      setLoading(prev => ({ ...prev, klydeWarrenPark: false }))
    }
  }

  const getLastSync = (tasks: any[]) => {
    if (!tasks || tasks.length === 0) return 'Never'
    const latest = tasks[0]
    const date = new Date(latest.created_at)
    const now = new Date()
    const diffHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffHours < 1) return 'Less than 1 hour ago'
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600'
      case 'running': return 'text-blue-600'
      case 'failed': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">📅 Bulk Event Import</h1>
          <p className="text-gray-600">
            Import events from Eventbrite, Ticketmaster, Dallas Arboretum, and Klyde Warren Park covering Dallas-Fort Worth area
          </p>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' ? 'bg-green-50 border border-green-200' :
            message.type === 'error' ? 'bg-red-50 border border-red-200' :
            'bg-blue-50 border border-blue-200'
          }`}>
            <p className={
              message.type === 'success' ? 'text-green-800' :
              message.type === 'error' ? 'text-red-800' :
              'text-blue-800'
            }>{message.text}</p>
          </div>
        )}

        {/* Real-time Progress Tracker */}
        {activeTask && (
          <div className="mb-6 bg-white border-2 border-blue-300 rounded-lg p-6 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">🔄 Sync in Progress</h3>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                activeTask.status === 'running' ? 'bg-blue-100 text-blue-700' :
                activeTask.status === 'completed' ? 'bg-green-100 text-green-700' :
                activeTask.status === 'failed' ? 'bg-red-100 text-red-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                {activeTask.status === 'running' ? '⏳ Running' :
                 activeTask.status === 'completed' ? '✅ Completed' :
                 activeTask.status === 'failed' ? '❌ Failed' :
                 '⏸️ Queued'}
              </span>
            </div>
            
            {activeTask.status === 'running' && (
              <div className="mb-4">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  <span className="text-gray-700">Processing organizers...</span>
                </div>
              </div>
            )}
            
            {/* Progress Bar */}
            {activeTask.status === 'running' && (
              <div className="mb-4">
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div 
                    className="bg-blue-600 h-3 rounded-full transition-all duration-500 animate-pulse"
                    style={{ width: '100%' }}
                  ></div>
                </div>
              </div>
            )}
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Task ID:</span>
                <span className="font-mono text-gray-900 font-semibold">#{activeTask.id}</span>
              </div>
              
              <div className="flex justify-between items-center bg-gradient-to-r from-blue-50 to-green-50 p-3 rounded-lg">
                <span className="text-gray-700 font-semibold">📊 Events Found:</span>
                <span className="font-bold text-blue-600 text-2xl">{activeTask.events_extracted || 0}</span>
              </div>
              
              {activeTask.status === 'running' && (
                <div className="text-center text-gray-600 animate-pulse">
                  <p>⏳ Processing organizers... Check back in 30-60 seconds</p>
                </div>
              )}
              
              {activeTask.status === 'completed' && (
                <div className="text-center text-green-600 font-semibold bg-green-50 p-3 rounded-lg">
                  ✅ Sync completed! {activeTask.events_extracted || 0} events imported
                </div>
              )}
              
              {activeTask.status === 'failed' && activeTask.error_message && (
                <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
                  <div className="flex items-start">
                    <span className="text-2xl mr-3">❌</span>
                    <div>
                      <h4 className="font-semibold text-red-700 mb-2">Sync Failed</h4>
                      <p className="text-sm text-red-600 font-mono bg-red-100 p-3 rounded">
                        {activeTask.error_message}
                      </p>
                      <p className="text-xs text-red-500 mt-2">
                        💡 Common issues: Missing API tokens, API rate limits, or network errors
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {activeTask.logs && activeTask.logs.length > 0 && (
                <details className="mt-3">
                  <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-900 mb-2">
                    📋 View detailed logs
                  </summary>
                  <div className="p-3 bg-gray-900 rounded-lg border border-gray-700">
                    <p className="text-xs text-green-400 font-mono whitespace-pre-wrap">{activeTask.logs.slice(-500)}</p>
                  </div>
                </details>
              )}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Eventbrite Sync Card */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mr-4">
                <span className="text-2xl">🟢</span>
              </div>
              <div>
                <h2 className="text-xl font-semibold">Eventbrite Events</h2>
                <p className="text-sm text-gray-500">Via Official API</p>
              </div>
            </div>
            
            <div className="mb-4 text-sm text-gray-600">
              <p className="mb-2">🏢 <strong>Sources:</strong></p>
              <ul className="list-disc list-inside ml-2 space-y-1">
                <li>Dallas Organizers</li>
                <li>Plano Venues</li>
                <li>Arlington Events</li>
                <li>Fort Worth Promoters</li>
              </ul>
              <p className="mt-3">📊 <strong>Expected:</strong> 50-150 events</p>
              <p className="mt-1">⏱️ <strong>Duration:</strong> 30-60 seconds</p>
            </div>

            {status && status.eventbrite && status.eventbrite.length > 0 && (
              <div className="mb-4 p-3 bg-gray-50 rounded text-sm">
                <p className="text-gray-600">
                  <strong>Last sync:</strong> {getLastSync(status.eventbrite)}
                </p>
                <p className={`mt-1 ${getStatusColor(status.eventbrite[0].status)}`}>
                  <strong>Status:</strong> {status.eventbrite[0].status}
                </p>
              </div>
            )}

            <button
              onClick={syncEventbriteEvents}
              disabled={loading.eventbrite}
              className="w-full py-3 px-4 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading.eventbrite ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Syncing...
                </span>
              ) : (
                '🟢 Sync Eventbrite Events'
              )}
            </button>
          </div>

          {/* Ticketmaster Sync Card */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mr-4">
                <span className="text-2xl">🎫</span>
              </div>
              <div>
                <h2 className="text-xl font-semibold">Ticketmaster Events</h2>
                <p className="text-sm text-gray-500">Via Official API</p>
              </div>
            </div>
            
            <div className="mb-4 text-sm text-gray-600">
              <p className="mb-2">🎭 <strong>Categories:</strong></p>
              <ul className="list-disc list-inside ml-2 space-y-1">
                <li>Music & Concerts</li>
                <li>Sports Events</li>
                <li>Arts & Theatre</li>
                <li>Family Entertainment</li>
              </ul>
              <p className="mt-3">📊 <strong>Expected:</strong> 100-300 events</p>
              <p className="mt-1">⏱️ <strong>Duration:</strong> 1-2 minutes</p>
            </div>

            {status && status.ticketmaster && status.ticketmaster.length > 0 && (
              <div className="mb-4 p-3 bg-gray-50 rounded text-sm">
                <p className="text-gray-600">
                  <strong>Last sync:</strong> {getLastSync(status.ticketmaster)}
                </p>
                <p className={`mt-1 ${getStatusColor(status.ticketmaster[0].status)}`}>
                  <strong>Status:</strong> {status.ticketmaster[0].status}
                </p>
              </div>
            )}

            <button
              onClick={syncTicketmasterEvents}
              disabled={loading.ticketmaster}
              className="w-full py-3 px-4 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading.ticketmaster ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Syncing...
                </span>
              ) : (
                '🎫 Sync Ticketmaster Events'
              )}
            </button>
          </div>

          {/* Dallas Arboretum Sync Card */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center mr-4">
                <span className="text-2xl">🌸</span>
              </div>
              <div>
                <h2 className="text-xl font-semibold">Dallas Arboretum</h2>
                <p className="text-sm text-gray-500">Family & Kids Events</p>
              </div>
            </div>
            
            <div className="mb-4 text-sm text-gray-600">
              <p className="mb-2">👨‍👩‍👧‍👦 <strong>Categories:</strong></p>
              <ul className="list-disc list-inside ml-2 space-y-1">
                <li>Family & Kids</li>
                <li>Nature & Gardens</li>
                <li>Educational Classes</li>
                <li>Holiday Events</li>
              </ul>
              <p className="mt-3">📊 <strong>Expected:</strong> 10-30 events</p>
              <p className="mt-1">⏱️ <strong>Duration:</strong> 15-30 seconds</p>
            </div>

            {status && status.dallas_arboretum && status.dallas_arboretum.length > 0 && (
              <div className="mb-4 p-3 bg-gray-50 rounded text-sm">
                <p className="text-gray-600">
                  <strong>Last sync:</strong> {getLastSync(status.dallas_arboretum)}
                </p>
                <p className={`mt-1 ${getStatusColor(status.dallas_arboretum[0].status)}`}>
                  <strong>Status:</strong> {status.dallas_arboretum[0].status}
                </p>
              </div>
            )}

            <button
              onClick={syncDallasArboretumEvents}
              disabled={loading.dallasArboretum}
              className="w-full py-3 px-4 bg-pink-600 text-white font-semibold rounded-lg hover:bg-pink-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading.dallasArboretum ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Syncing...
                </span>
              ) : (
                '🌸 Sync Dallas Arboretum'
              )}
            </button>
          </div>

          {/* Klyde Warren Park Sync Card */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mr-4">
                <span className="text-2xl">🌳</span>
              </div>
              <div>
                <h2 className="text-xl font-semibold">Klyde Warren Park</h2>
                <p className="text-sm text-gray-500">Community Events</p>
              </div>
            </div>
            
            <div className="mb-4 text-sm text-gray-600">
              <p className="mb-2">🎉 <strong>Categories:</strong></p>
              <ul className="list-disc list-inside ml-2 space-y-1">
                <li>Music & Concerts</li>
                <li>Movies & Film</li>
                <li>Family & Kids</li>
                <li>Food & Dining</li>
                <li>Arts & Theatre</li>
              </ul>
              <p className="mt-3">📊 <strong>Expected:</strong> 30-50 events</p>
              <p className="mt-1">⏱️ <strong>Duration:</strong> 30-60 seconds</p>
            </div>

            {status && status.klyde_warren_park && status.klyde_warren_park.length > 0 && (
              <div className="mb-4 p-3 bg-gray-50 rounded text-sm">
                <p className="text-gray-600">
                  <strong>Last sync:</strong> {getLastSync(status.klyde_warren_park)}
                </p>
                <p className={`mt-1 ${getStatusColor(status.klyde_warren_park[0].status)}`}>
                  <strong>Status:</strong> {status.klyde_warren_park[0].status}
                </p>
              </div>
            )}

            <button
              onClick={syncKlydeWarrenParkEvents}
              disabled={loading.klydeWarrenPark}
              className="w-full py-3 px-4 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading.klydeWarrenPark ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Syncing...
                </span>
              ) : (
                '🌳 Sync Klyde Warren Park'
              )}
            </button>
          </div>
        </div>

        {/* Info Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            💡 <span className="ml-2">Tips</span>
          </h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>• Events are automatically deduplicated - no worries about duplicates!</li>
            <li>• Eventbrite syncs from configured Dallas-area organizers</li>
            <li>• Ticketmaster covers concerts, sports, theatre, and family events</li>
            <li>• Dallas Arboretum focuses on family-friendly and kids events</li>
            <li>• Klyde Warren Park features community events, movies, music, and more</li>
            <li>• You can run all syncs simultaneously</li>
            <li>• Check the Events page to see imported events</li>
          </ul>
        </div>

        <div className="mt-6 text-center">
          <button
            onClick={() => router.push('/events')}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            → View All Events
          </button>
        </div>
      </div>
    </div>
  )
}
