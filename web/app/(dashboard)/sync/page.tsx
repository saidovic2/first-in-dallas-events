'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function BulkSyncPage() {
  const router = useRouter()
  const [loading, setLoading] = useState<{facebook: boolean, eventbrite: boolean}>({
    facebook: false,
    eventbrite: false
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
      const response = await fetch('http://localhost:8001/api/sync/status', {
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

  const syncFacebookEvents = async () => {
    setLoading(prev => ({ ...prev, facebook: true }))
    setMessage(null)
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8001/api/sync/facebook/dallas', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setMessage({
          type: 'success',
          text: `✅ ${data.message}! Searching in Dallas, Plano, Arlington, and Fort Worth. This may take 2-3 minutes.`
        })
        // Refresh status after a short delay
        setTimeout(fetchSyncStatus, 2000)
      } else {
        throw new Error('Failed to start sync')
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: '❌ Error starting Facebook sync. Please try again.'
      })
    } finally {
      setLoading(prev => ({ ...prev, facebook: false }))
    }
  }

  const pollTaskStatus = async (taskId: number) => {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://localhost:8001/api/tasks/${taskId}`, {
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
            text: `✅ Sync completed! Found ${task.events_extracted} events from 20 organizers.`
          })
        } else {
          setMessage({
            type: 'error',
            text: `❌ Sync failed: ${task.error_message || 'Unknown error'}`
          })
        }
        
        setTimeout(() => setActiveTask(null), 5000)
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
      const response = await fetch('http://localhost:8001/api/sync/eventbrite/dallas', {
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
        
        // Start polling for task status
        if (data.task_id) {
          const interval = setInterval(() => pollTaskStatus(data.task_id), 2000)
          setPollingInterval(interval)
        }
        
        setTimeout(fetchSyncStatus, 2000)
      } else {
        throw new Error('Failed to start sync')
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: '❌ Error starting Eventbrite sync. Please try again.'
      })
      setLoading(prev => ({ ...prev, eventbrite: false }))
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
            Import hundreds of events from Dallas, Plano, Arlington, and Fort Worth with one click
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
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Task ID:</span>
                <span className="font-mono text-gray-900">#{activeTask.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Events Found:</span>
                <span className="font-bold text-blue-600 text-lg">{activeTask.events_extracted || 0}</span>
              </div>
              {activeTask.logs && (
                <div className="mt-3 p-3 bg-gray-50 rounded border border-gray-200">
                  <p className="text-xs text-gray-600 font-mono whitespace-pre-wrap">{activeTask.logs.slice(-200)}</p>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Facebook Sync Card */}
          <div className="bg-white border-2 border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                <span className="text-2xl">🔵</span>
              </div>
              <div>
                <h2 className="text-xl font-semibold">Facebook Events</h2>
                <p className="text-sm text-gray-500">Via Apify</p>
              </div>
            </div>
            
            <div className="mb-4 text-sm text-gray-600">
              <p className="mb-2">📍 <strong>Locations:</strong></p>
              <ul className="list-disc list-inside ml-2 space-y-1">
                <li>Dallas, TX</li>
                <li>Plano, TX</li>
                <li>Arlington, TX</li>
                <li>Fort Worth, TX</li>
              </ul>
              <p className="mt-3">📊 <strong>Expected:</strong> 200-400 events</p>
              <p className="mt-1">⏱️ <strong>Duration:</strong> 2-3 minutes</p>
            </div>

            {status && status.facebook && status.facebook.length > 0 && (
              <div className="mb-4 p-3 bg-gray-50 rounded text-sm">
                <p className="text-gray-600">
                  <strong>Last sync:</strong> {getLastSync(status.facebook)}
                </p>
                <p className={`mt-1 ${getStatusColor(status.facebook[0].status)}`}>
                  <strong>Status:</strong> {status.facebook[0].status}
                </p>
              </div>
            )}

            <button
              onClick={syncFacebookEvents}
              disabled={loading.facebook}
              className="w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading.facebook ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  Syncing...
                </span>
              ) : (
                '🔵 Sync Facebook Events'
              )}
            </button>
          </div>

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
        </div>

        {/* Info Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            💡 <span className="ml-2">Tips</span>
          </h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>• Events are automatically deduplicated - no worries about duplicates!</li>
            <li>• Facebook sync searches 4 cities and can take 2-3 minutes</li>
            <li>• Eventbrite sync is faster but requires configured organizers</li>
            <li>• You can run both syncs simultaneously</li>
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
