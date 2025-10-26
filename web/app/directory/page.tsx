'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { eventsApi } from '@/lib/api'
import { formatDateTime } from '@/lib/utils'
import { Calendar, MapPin, DollarSign, Grid, List, Search } from 'lucide-react'
import Image from 'next/image'

export default function DirectoryPage() {
  const [events, setEvents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [filters, setFilters] = useState({
    search: '',
    city: '',
    price_tier: '',
    date_range: ''
  })
  const [cities, setCities] = useState<string[]>([])
  const [categories, setCategories] = useState<string[]>([])

  useEffect(() => {
    loadEvents()
    loadFilters()
  }, [])

  const getDateRange = (range: string) => {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    
    switch (range) {
      case 'today':
        return {
          start: today.toISOString(),
          end: new Date(today.getTime() + 24 * 60 * 60 * 1000).toISOString()
        }
      case 'tomorrow':
        const tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000)
        return {
          start: tomorrow.toISOString(),
          end: new Date(tomorrow.getTime() + 24 * 60 * 60 * 1000).toISOString()
        }
      case 'this_week': {
        const dayOfWeek = now.getDay()
        const startOfWeek = new Date(today.getTime() - dayOfWeek * 24 * 60 * 60 * 1000)
        const endOfWeek = new Date(startOfWeek.getTime() + 7 * 24 * 60 * 60 * 1000)
        return {
          start: startOfWeek.toISOString(),
          end: endOfWeek.toISOString()
        }
      }
      case 'this_weekend': {
        const dayOfWeek = now.getDay()
        const friday = new Date(today.getTime() + (5 - dayOfWeek) * 24 * 60 * 60 * 1000)
        const monday = new Date(friday.getTime() + 3 * 24 * 60 * 60 * 1000)
        return {
          start: friday.toISOString(),
          end: monday.toISOString()
        }
      }
      case 'next_week': {
        const dayOfWeek = now.getDay()
        const nextWeekStart = new Date(today.getTime() + (7 - dayOfWeek) * 24 * 60 * 60 * 1000)
        const nextWeekEnd = new Date(nextWeekStart.getTime() + 7 * 24 * 60 * 60 * 1000)
        return {
          start: nextWeekStart.toISOString(),
          end: nextWeekEnd.toISOString()
        }
      }
      case 'this_month':
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
        const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59)
        return {
          start: startOfMonth.toISOString(),
          end: endOfMonth.toISOString()
        }
      default:
        return null
    }
  }

  const loadEvents = async () => {
    try {
      const params: any = { status: 'PUBLISHED' }
      if (filters.search) params.search = filters.search
      if (filters.city) params.city = filters.city
      if (filters.price_tier) params.price_tier = filters.price_tier
      
      if (filters.date_range) {
        const dateRange = getDateRange(filters.date_range)
        if (dateRange) {
          params.start_date = dateRange.start
          params.end_date = dateRange.end
        }
      }
      
      const response = await eventsApi.list(params)
      setEvents(response.data)
    } catch (error) {
      console.error('Failed to load events:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadFilters = async () => {
    try {
      const [citiesRes, categoriesRes] = await Promise.all([
        eventsApi.getCities(),
        eventsApi.getCategories()
      ])
      setCities(citiesRes.data)
      setCategories(categoriesRes.data)
    } catch (error) {
      console.error('Failed to load filters:', error)
    }
  }

  const handleFilterChange = (key: string, value: string) => {
    setFilters({ ...filters, [key]: value })
  }

  const applyFilters = () => {
    loadEvents()
  }

  const clearFilters = () => {
    setFilters({ search: '', city: '', price_tier: '', date_range: '' })
    setTimeout(loadEvents, 100)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <h1 className="text-4xl font-bold text-gray-900">Upcoming Events</h1>
          <p className="text-gray-600 mt-2">Discover local events happening near you</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Filters */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="md:col-span-2">
                <Input
                  placeholder="Search events..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && applyFilters()}
                />
              </div>
              <select
                className="px-3 py-2 border rounded-md"
                value={filters.date_range}
                onChange={(e) => handleFilterChange('date_range', e.target.value)}
              >
                <option value="">All Dates</option>
                <option value="today">📅 Today</option>
                <option value="tomorrow">🌅 Tomorrow</option>
                <option value="this_weekend">🎉 This Weekend</option>
                <option value="this_week">📆 This Week</option>
                <option value="next_week">➡️ Next Week</option>
                <option value="this_month">📋 This Month</option>
              </select>
              <select
                className="px-3 py-2 border rounded-md"
                value={filters.city}
                onChange={(e) => handleFilterChange('city', e.target.value)}
              >
                <option value="">All Cities</option>
                {cities.map(city => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
              <select
                className="px-3 py-2 border rounded-md"
                value={filters.price_tier}
                onChange={(e) => handleFilterChange('price_tier', e.target.value)}
              >
                <option value="">All Prices</option>
                <option value="free">Free</option>
                <option value="paid">Paid</option>
              </select>
            </div>
            <div className="flex justify-between items-center mt-4">
              <div className="flex gap-2">
                <Button onClick={applyFilters}>
                  <Search className="h-4 w-4 mr-2" />
                  Apply Filters
                </Button>
                <Button variant="outline" onClick={clearFilters}>
                  Clear
                </Button>
              </div>
              <div className="flex gap-2">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'outline'}
                  size="icon"
                  onClick={() => setViewMode('grid')}
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'outline'}
                  size="icon"
                  onClick={() => setViewMode('list')}
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Events */}
        {events.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-gray-500">No events found</p>
            </CardContent>
          </Card>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {events.map((event) => (
              <Card key={event.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                {event.image_url && (
                  <div className="relative h-48 w-full">
                    <Image
                      src={event.image_url}
                      alt={event.title}
                      fill
                      className="object-cover"
                    />
                  </div>
                )}
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                      {event.title}
                    </h3>
                  </div>
                  
                  <div className="space-y-2 text-sm text-gray-600 mb-4">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>{formatDateTime(event.start_at)}</span>
                    </div>
                    {event.venue && (
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4" />
                        <span>{event.venue}{event.city && `, ${event.city}`}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <DollarSign className="h-4 w-4" />
                      <span className="capitalize">{event.price_tier}</span>
                    </div>
                  </div>

                  <Button
                    className="w-full mt-4"
                    onClick={() => {
                      if (event.source_url && event.source_url.startsWith('http')) {
                        window.open(event.source_url, '_blank')
                      } else {
                        alert(`Event: ${event.title}\n\nLocation: ${event.city}\n\nDate: ${new Date(event.start_time).toLocaleString()}\n\n${event.description ? event.description.substring(0, 200) + '...' : 'No description available'}`)  
                      }
                    }}
                    disabled={!event.source_url || !event.source_url.startsWith('http')}
                  >
                    {event.source_url && event.source_url.startsWith('http') ? 'View Details' : 'Details'}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {events.map((event) => (
              <Card key={event.id}>
                <CardContent className="p-6">
                  <div className="flex gap-6">
                    {event.image_url && (
                      <div className="relative w-48 h-32 flex-shrink-0 rounded-lg overflow-hidden">
                        <Image
                          src={event.image_url}
                          alt={event.title}
                          fill
                          className="object-cover"
                        />
                      </div>
                    )}
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">{event.title}</h3>
                      <div className="space-y-1 text-sm text-gray-600 mb-4">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          <span>{formatDateTime(event.start_at)}</span>
                        </div>
                        {event.venue && (
                          <div className="flex items-center gap-2">
                            <MapPin className="h-4 w-4" />
                            <span>{event.venue}{event.city && `, ${event.city}`}</span>
                          </div>
                        )}
                      </div>
                      {event.description && (
                        <p className="text-sm text-gray-600 line-clamp-2 mb-4">
                          {event.description}
                        </p>
                      )}
                      <Button 
                        onClick={() => {
                          if (event.source_url && event.source_url.startsWith('http')) {
                            window.open(event.source_url, '_blank')
                          } else {
                            alert(`Event: ${event.title}\n\nLocation: ${event.city}\n\nDate: ${new Date(event.start_time).toLocaleString()}\n\n${event.description ? event.description.substring(0, 200) + '...' : 'No description available'}`)
                          }
                        }}
                        disabled={!event.source_url || !event.source_url.startsWith('http')}
                      >
                        {event.source_url && event.source_url.startsWith('http') ? 'View Details' : 'Details'}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
