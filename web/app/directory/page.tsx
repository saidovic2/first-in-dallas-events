'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { eventsApi } from '@/lib/api'
import { formatDateTime } from '@/lib/utils'
import { Calendar, MapPin, DollarSign, Grid, List, Search, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react'
import Image from 'next/image'
import { format } from 'date-fns'

export default function DirectoryPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  
  const [allEvents, setAllEvents] = useState<any[]>([])
  const [displayedEvents, setDisplayedEvents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const itemsPerPage = 20
  
  // Get today's date in YYYY-MM-DD format
  const getTodayDate = () => {
    const today = new Date()
    return format(today, 'yyyy-MM-dd')
  }
  
  const [filters, setFilters] = useState({
    search: '',
    city: '',
    price_tier: '',
    date: getTodayDate()
  })
  const [cities, setCities] = useState<string[]>([])

  useEffect(() => {
    // Load filters from URL on mount
    const search = searchParams.get('search') || ''
    const city = searchParams.get('city') || ''
    const price_tier = searchParams.get('price_tier') || ''
    const date = searchParams.get('date') || getTodayDate()
    const page = parseInt(searchParams.get('page') || '1')
    
    setFilters({ search, city, price_tier, date })
    setCurrentPage(page)
    loadFilters()
  }, [])
  
  useEffect(() => {
    if (cities.length > 0) {
      loadEvents()
    }
  }, [filters, currentPage])

  const updateURL = (newFilters: any, page: number) => {
    const params = new URLSearchParams()
    if (newFilters.search) params.set('search', newFilters.search)
    if (newFilters.city) params.set('city', newFilters.city)
    if (newFilters.price_tier) params.set('price_tier', newFilters.price_tier)
    if (newFilters.date) params.set('date', newFilters.date)
    if (page > 1) params.set('page', page.toString())
    
    router.push(`?${params.toString()}`, { scroll: false })
  }

  const loadEvents = async () => {
    setLoading(true)
    try {
      const params: any = { status: 'PUBLISHED', limit: 1000 }
      if (filters.search) params.search = filters.search
      if (filters.city) params.city = filters.city
      if (filters.price_tier) params.price_tier = filters.price_tier
      
      // If date is selected, filter by that specific day
      if (filters.date) {
        const selectedDate = new Date(filters.date)
        const startOfDay = new Date(selectedDate.setHours(0, 0, 0, 0))
        const endOfDay = new Date(selectedDate.setHours(23, 59, 59, 999))
        params.start_date = startOfDay.toISOString()
        params.end_date = endOfDay.toISOString()
      }
      
      const response = await eventsApi.list(params)
      const events = response.data
      setAllEvents(events)
      
      // Calculate pagination
      const total = Math.ceil(events.length / itemsPerPage)
      setTotalPages(total)
      
      // Get events for current page
      const startIdx = (currentPage - 1) * itemsPerPage
      const endIdx = startIdx + itemsPerPage
      setDisplayedEvents(events.slice(startIdx, endIdx))
      
      updateURL(filters, currentPage)
    } catch (error) {
      console.error('Failed to load events:', error)
      setAllEvents([])
      setDisplayedEvents([])
    } finally {
      setLoading(false)
    }
  }

  const loadFilters = async () => {
    try {
      const citiesRes = await eventsApi.getCities()
      setCities(citiesRes.data)
    } catch (error) {
      console.error('Failed to load filters:', error)
    }
  }

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    setCurrentPage(1) // Reset to page 1 when filter changes
  }

  const applyFilters = () => {
    setCurrentPage(1)
    loadEvents()
  }

  const clearFilters = () => {
    const newFilters = { search: '', city: '', price_tier: '', date: getTodayDate() }
    setFilters(newFilters)
    setCurrentPage(1)
  }
  
  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  
  const generatePageNumbers = () => {
    const pages = []
    const maxVisible = 5
    
    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i)
        pages.push('...')
        pages.push(totalPages)
      } else if (currentPage >= totalPages - 2) {
        pages.push(1)
        pages.push('...')
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i)
      } else {
        pages.push(1)
        pages.push('...')
        pages.push(currentPage - 1)
        pages.push(currentPage)
        pages.push(currentPage + 1)
        pages.push('...')
        pages.push(totalPages)
      }
    }
    
    return pages
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
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="md:col-span-1">
                <Input
                  placeholder="Search events..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && applyFilters()}
                />
              </div>
              <div>
                <select
                  className="w-full px-3 py-2 border rounded-md"
                  value={filters.city}
                  onChange={(e) => handleFilterChange('city', e.target.value)}
                >
                  <option value="">All Cities</option>
                  {cities.map(city => (
                    <option key={city} value={city}>{city}</option>
                  ))}
                </select>
              </div>
              <div>
                <Input
                  type="date"
                  value={filters.date}
                  onChange={(e) => handleFilterChange('date', e.target.value)}
                  className="w-full"
                />
              </div>
              <div>
                <select
                  className="w-full px-3 py-2 border rounded-md"
                  value={filters.price_tier}
                  onChange={(e) => handleFilterChange('price_tier', e.target.value)}
                >
                  <option value="">All Prices</option>
                  <option value="free">Free</option>
                  <option value="paid">Paid</option>
                </select>
              </div>
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
        {displayedEvents.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-gray-500 text-lg">
                {filters.date 
                  ? "No events found for this day. Try another date." 
                  : "No events found"}
              </p>
            </CardContent>
          </Card>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {displayedEvents.map((event) => (
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
            {displayedEvents.map((event) => (
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
        
        {/* Pagination */}
        {totalPages > 1 && displayedEvents.length > 0 && (
          <Card className="mt-8">
            <CardContent className="py-4">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, allEvents.length)} of {allEvents.length} events
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => handlePageChange(1)}
                    disabled={currentPage === 1}
                    title="First page"
                  >
                    <ChevronsLeft className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    title="Previous page"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  
                  <div className="flex gap-1">
                    {generatePageNumbers().map((page, idx) => (
                      page === '...' ? (
                        <span key={`ellipsis-${idx}`} className="px-3 py-2 text-gray-500">
                          ...
                        </span>
                      ) : (
                        <Button
                          key={page}
                          variant={currentPage === page ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => handlePageChange(page as number)}
                          className="min-w-[40px]"
                        >
                          {page}
                        </Button>
                      )
                    ))}
                  </div>
                  
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    title="Next page"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => handlePageChange(totalPages)}
                    disabled={currentPage === totalPages}
                    title="Last page"
                  >
                    <ChevronsRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
