'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { eventsApi } from '@/lib/api'
import { formatDateTime } from '@/lib/utils'
import { Search, Edit, Trash2, ExternalLink, Upload, CheckSquare, Square, CalendarX } from 'lucide-react'
import Image from 'next/image'
import api from '@/lib/api'

export default function EventsPage() {
  const [events, setEvents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [cityFilter, setCityFilter] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [priceTierFilter, setPriceTierFilter] = useState('')
  const [selectedEvents, setSelectedEvents] = useState<Set<number>>(new Set())
  const [cities, setCities] = useState<string[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [bulkActionLoading, setBulkActionLoading] = useState(false)
  const [eventCounts, setEventCounts] = useState({ draft: 0, published: 0, total: 0 })
  const [cleanupLoading, setCleanupLoading] = useState(false)

  useEffect(() => {
    loadEvents()
    loadCities()
    loadCategories()
    loadEventCounts()
  }, [statusFilter, cityFilter, categoryFilter, priceTierFilter])

  const loadEventCounts = async () => {
    try {
      const [draftRes, publishedRes, totalRes] = await Promise.all([
        eventsApi.list({ status: 'DRAFT' }),
        eventsApi.list({ status: 'PUBLISHED' }),
        eventsApi.list({})
      ])
      setEventCounts({
        draft: draftRes.data.length,
        published: publishedRes.data.length,
        total: totalRes.data.length
      })
    } catch (error) {
      console.error('Failed to load event counts:', error)
    }
  }

  const loadEvents = async () => {
    try {
      const params: any = {}
      if (statusFilter) params.status = statusFilter
      if (search) params.search = search
      if (cityFilter) params.city = cityFilter
      if (categoryFilter) params.category = categoryFilter
      if (priceTierFilter) params.price_tier = priceTierFilter
      
      // Only show future events (scrapers will filter out past events)
      // params.include_past = false  // Default behavior
      
      const response = await eventsApi.list(params)
      setEvents(response.data)
    } catch (error) {
      console.error('Failed to load events:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadCities = async () => {
    try {
      const response = await eventsApi.getCities()
      setCities(response.data)
    } catch (error) {
      console.error('Failed to load cities:', error)
    }
  }

  const loadCategories = async () => {
    try {
      const response = await eventsApi.getCategories()
      setCategories(response.data)
    } catch (error) {
      console.error('Failed to load categories:', error)
    }
  }

  const handleSearch = () => {
    loadEvents()
  }

  const handleCleanupPastEvents = async () => {
    if (!confirm('Delete all past events (older than 7 days)? This action cannot be undone.')) return

    setCleanupLoading(true)
    try {
      const response = await api.post('/api/events/cleanup/past-events?days_old=7')
      const { deleted_count } = response.data
      alert(`✅ Successfully deleted ${deleted_count} past events`)
      loadEvents()
      loadEventCounts()
    } catch (error: any) {
      console.error('Failed to cleanup:', error)
      alert(`Failed to cleanup past events: ${error.response?.data?.detail || error.message}`)
    } finally {
      setCleanupLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this event?')) return
    
    try {
      await eventsApi.delete(id)
      setEvents(events.filter(e => e.id !== id))
    } catch (error) {
      console.error('Failed to delete event:', error)
    }
  }

  const handlePublish = async (id: number) => {
    try {
      await eventsApi.publish(id)
      alert('Event published to WordPress successfully!')
      loadEvents()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to publish event')
    }
  }

  const handleStatusChange = async (id: number, status: string) => {
    try {
      await eventsApi.update(id, { status })
      loadEvents()
    } catch (error) {
      console.error('Failed to update status:', error)
    }
  }

  const toggleSelectEvent = (id: number) => {
    const newSelected = new Set(selectedEvents)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedEvents(newSelected)
  }

  const toggleSelectAll = () => {
    if (selectedEvents.size === events.length) {
      setSelectedEvents(new Set())
    } else {
      setSelectedEvents(new Set(events.map(e => e.id)))
    }
  }

  const handleBulkPublish = async () => {
    if (selectedEvents.size === 0) {
      alert('Please select at least one event')
      return
    }

    if (!confirm(`Are you sure you want to publish ${selectedEvents.size} events to the public directory?`)) {
      return
    }

    setBulkActionLoading(true)
    try {
      const eventIdsArray = Array.from(selectedEvents)
      console.log('Sending event IDs:', eventIdsArray)
      
      const response = await eventsApi.bulkPublish(eventIdsArray)
      console.log('Bulk publish response:', response)
      console.log('Response data:', response.data)
      
      // Extract count safely
      let count = selectedEvents.size
      if (response.data?.published_count) {
        count = response.data.published_count
      }
      
      alert(`✅ Success! Published ${count} events to the directory!`)
      setSelectedEvents(new Set())
      loadEvents()
      loadEventCounts()
    } catch (error: any) {
      console.error('Bulk publish error - Full error:', error)
      console.error('Error response:', error.response)
      console.error('Error response data:', error.response?.data)
      
      let errorMsg = 'Failed to bulk publish events'
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMsg = error.response.data.detail
        } else if (Array.isArray(error.response.data.detail)) {
          errorMsg = JSON.stringify(error.response.data.detail)
        } else {
          errorMsg = JSON.stringify(error.response.data.detail)
        }
      } else if (error.message) {
        errorMsg = error.message
      }
      
      alert(`❌ Error: ${errorMsg}`)
    } finally {
      setBulkActionLoading(false)
    }
  }

  const handleBulkDelete = async () => {
    if (selectedEvents.size === 0) {
      alert('Please select at least one event')
      return
    }

    if (!confirm(`Are you sure you want to delete ${selectedEvents.size} events? This cannot be undone.`)) {
      return
    }

    setBulkActionLoading(true)
    try {
      const response = await eventsApi.bulkDelete(Array.from(selectedEvents))
      alert(response.data.message)
      setSelectedEvents(new Set())
      loadEvents()
      loadEventCounts()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to bulk delete events')
    } finally {
      setBulkActionLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Manage Events</h1>
          <p className="text-gray-600 mt-1">Review, edit, and publish your events</p>
          <div className="flex gap-4 mt-4">
            <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-lg">
              <span className="text-2xl font-bold text-blue-600">{eventCounts.total}</span>
              <span className="text-sm text-gray-600">Total Events</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-orange-50 rounded-lg">
              <span className="text-2xl font-bold text-orange-600">{eventCounts.draft}</span>
              <span className="text-sm text-gray-600">Draft</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-lg">
              <span className="text-2xl font-bold text-green-600">{eventCounts.published}</span>
              <span className="text-sm text-gray-600">Published</span>
            </div>
          </div>
        </div>
        
        {/* Cleanup Button */}
        <Button
          onClick={handleCleanupPastEvents}
          disabled={cleanupLoading}
          variant="outline"
          className="text-red-600 border-red-300 hover:bg-red-50"
        >
          {cleanupLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600 mr-2"></div>
              Cleaning...
            </>
          ) : (
            <>
              <CalendarX className="h-4 w-4 mr-2" />
              Delete Past Events
            </>
          )}
        </Button>
      </div>

      {/* Bulk Actions */}
      {selectedEvents.size > 0 && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="font-medium text-blue-900">
                  {selectedEvents.size} event(s) selected
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedEvents(new Set())}
                >
                  Clear Selection
                </Button>
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={handleBulkPublish}
                  disabled={bulkActionLoading}
                  className="bg-green-600 hover:bg-green-700"
                >
                  📢 Publish Selected to Directory
                </Button>
                <Button
                  onClick={handleBulkDelete}
                  disabled={bulkActionLoading}
                  variant="destructive"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Selected
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="flex gap-4">
            <div className="flex-1 flex gap-2">
              <Input
                placeholder="Search events..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button onClick={handleSearch}>
                <Search className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="flex gap-4 flex-wrap">
            <select
              className="px-3 py-2 border rounded-md"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All Status</option>
              <option value="DRAFT">Draft</option>
              <option value="PUBLISHED">Published</option>
            </select>
            <select
              className="px-3 py-2 border rounded-md"
              value={cityFilter}
              onChange={(e) => setCityFilter(e.target.value)}
            >
              <option value="">All Cities</option>
              {cities.map(city => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>
            <select
              className="px-3 py-2 border rounded-md"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            <select
              className="px-3 py-2 border rounded-md"
              value={priceTierFilter}
              onChange={(e) => setPriceTierFilter(e.target.value)}
            >
              <option value="">All Prices</option>
              <option value="free">Free</option>
              <option value="paid">Paid</option>
              <option value="donation">Donation</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Select All */}
      {events.length > 0 && (
        <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 rounded-lg">
          <button
            onClick={toggleSelectAll}
            className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            {selectedEvents.size === events.length ? (
              <CheckSquare className="h-5 w-5 text-blue-600" />
            ) : (
              <Square className="h-5 w-5" />
            )}
            Select All ({events.length} events)
          </button>
        </div>
      )}

      {/* Events List */}
      <div className="space-y-4">
        {events.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-gray-500">No events found</p>
            </CardContent>
          </Card>
        ) : (
          events.map((event) => (
            <Card key={event.id} className={selectedEvents.has(event.id) ? 'ring-2 ring-blue-500' : ''}>
              <CardContent className="p-6">
                <div className="flex gap-6">
                  {/* Checkbox */}
                  <div className="flex items-start pt-2">
                    <button
                      onClick={() => toggleSelectEvent(event.id)}
                      className="text-gray-400 hover:text-blue-600"
                    >
                      {selectedEvents.has(event.id) ? (
                        <CheckSquare className="h-6 w-6 text-blue-600" />
                      ) : (
                        <Square className="h-6 w-6" />
                      )}
                    </button>
                  </div>
                  <div className="relative w-48 h-32 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100">
                    {event.image_url ? (
                      <Image
                        src={event.image_url}
                        alt={event.title}
                        fill
                        className="object-cover"
                        unoptimized
                        onError={(e) => {
                          console.error('Image load error:', event.image_url);
                          e.currentTarget.style.display = 'none';
                        }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
                        <div className="text-center text-gray-400">
                          <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <span className="text-xs">No Image</span>
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900">{event.title}</h3>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant={event.status === 'published' ? 'default' : 'secondary'}>
                            {event.status}
                          </Badge>
                          <Badge variant="outline">{event.source_type}</Badge>
                          {event.category && (
                            <Badge variant="outline">{event.category}</Badge>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => window.open(event.source_url, '_blank')}
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => handleDelete(event.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="mt-4 space-y-2 text-sm text-gray-600">
                      <div>
                        <strong>Date:</strong> {formatDateTime(event.start_at)}
                        {event.end_at && ` - ${formatDateTime(event.end_at)}`}
                      </div>
                      {event.venue && (
                        <div>
                          <strong>Venue:</strong> {event.venue}
                          {event.city && `, ${event.city}`}
                        </div>
                      )}
                      {event.description && (
                        <div className="line-clamp-2">
                          <strong>Description:</strong> {event.description}
                        </div>
                      )}
                    </div>

                    <div className="mt-4 flex gap-2">
                      {event.status === 'DRAFT' && (
                        <Button
                          size="sm"
                          onClick={() => handleStatusChange(event.id, 'PUBLISHED')}
                        >
                          Publish to Directory
                        </Button>
                      )}
                      {event.status === 'PUBLISHED' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleStatusChange(event.id, 'DRAFT')}
                        >
                          Unpublish
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handlePublish(event.id)}
                      >
                        <Upload className="h-4 w-4 mr-2" />
                        Push to WordPress
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
