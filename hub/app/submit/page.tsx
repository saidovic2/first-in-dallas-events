'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { submissionsApi, checkoutApi } from '@/lib/api'
import { Nav } from '@/components/layout/nav'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Check, ChevronLeft, ChevronRight, Loader2, Star, Calendar, MapPin } from 'lucide-react'

// ── Pricing constants (kept in sync with api/pricing.py) ─────────────────────
const SINGLE_PRICE = 19
const UNLIMITED_PRICE = 49
const FEATURED_PRICE = 29

const STEPS = [
  { id: 1, name: 'Event Details', description: 'Title, URL, format' },
  { id: 2, name: 'Date & Location', description: 'Venue, date & details' },
  { id: 3, name: 'Payment', description: 'Choose plan & complete' },
]

// ── Mini event preview card (used in the featured comparison) ─────────────────
function EventPreviewCard({
  title,
  startDate,
  venue,
  city,
  featured = false,
}: {
  title: string
  startDate: string
  venue: string
  city: string
  featured?: boolean
}) {
  const displayDate = startDate
    ? new Date(startDate).toLocaleDateString('en-US', {
        weekday: 'short', month: 'short', day: 'numeric',
      })
    : 'Date TBD'

  return (
    <div
      className={`rounded-lg border p-3 text-sm ${
        featured
          ? 'border-amber-400 bg-amber-50 shadow-md'
          : 'border-gray-200 bg-white'
      }`}
    >
      {featured && (
        <div className="flex items-center gap-1 mb-2">
          <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
          <span className="text-xs font-bold text-amber-700 uppercase tracking-wide">
            Featured — Top of Calendar
          </span>
        </div>
      )}
      <p className={`font-semibold leading-tight mb-1 ${featured ? 'text-amber-900' : 'text-gray-900'}`}>
        {title || 'Your Event Title'}
      </p>
      <div className="flex items-center gap-1 text-gray-500 mb-0.5">
        <Calendar className="w-3 h-3" />
        <span className="text-xs">{displayDate}</span>
      </div>
      {(venue || city) && (
        <div className="flex items-center gap-1 text-gray-500">
          <MapPin className="w-3 h-3" />
          <span className="text-xs">{[venue, city].filter(Boolean).join(', ')}</span>
        </div>
      )}
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function SubmitPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(1)
  const [user, setUser] = useState<any>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Event form data (steps 1–2)
  const [formData, setFormData] = useState({
    title: '',
    primary_url: '',
    format: 'in-person' as 'in-person' | 'online' | 'hybrid',
    country: 'USA',
    venue: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    start_date: '',
    end_date: '',
    price: '',
    price_tier: 'free' as 'free' | 'paid',
    image_url: '',
    description: '',
    organizer_contact: '',
  })

  const [imagePreview, setImagePreview] = useState('')
  const [uploading, setUploading] = useState(false)

  // Payment step state
  const [plan, setPlan] = useState<'single' | 'unlimited'>('single')
  const [featuredChecked, setFeaturedChecked] = useState(false)
  const [pendingEventId, setPendingEventId] = useState<number | null>(null)
  const [savingPending, setSavingPending] = useState(false)
  const [checkingOut, setCheckingOut] = useState(false)

  useEffect(() => {
    checkUser()
  }, [])

  const checkUser = async () => {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) { router.push('/auth/login'); return }
    setUser(user)
    setFormData(prev => ({ ...prev, organizer_contact: user.email! }))
  }

  const updateField = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) setErrors(prev => ({ ...prev, [field]: '' }))
  }

  // ── Validation ─────────────────────────────────────────────────────────────
  const validateStep1 = () => {
    const e: Record<string, string> = {}
    if (!formData.title.trim()) e.title = 'Event title is required'
    if (!formData.format) e.format = 'Event format is required'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const validateStep2 = () => {
    const e: Record<string, string> = {}
    if (!formData.city.trim()) e.city = 'City is required'
    if (!formData.start_date) e.start_date = 'Start date is required'
    if (!formData.description.trim()) e.description = 'Description is required'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  // ── Image upload ───────────────────────────────────────────────────────────
  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.type.startsWith('image/')) { setErrors({ ...errors, image: 'Please upload an image file' }); return }
    if (file.size > 5 * 1024 * 1024) { setErrors({ ...errors, image: 'Image must be less than 5MB' }); return }

    const reader = new FileReader()
    reader.onloadend = () => setImagePreview(reader.result as string)
    reader.readAsDataURL(file)

    setUploading(true)
    try {
      const fileExt = file.name.split('.').pop()
      const fileName = `${user.id}-${Date.now()}.${fileExt}`
      const filePath = `event-images/${fileName}`
      const { error: uploadError } = await supabase.storage.from('events').upload(filePath, file)
      if (uploadError) throw uploadError
      const { data } = supabase.storage.from('events').getPublicUrl(filePath)
      updateField('image_url', data.publicUrl)
    } catch (err: any) {
      setErrors({ ...errors, image: 'Failed to upload image. You can continue without one.' })
    } finally {
      setUploading(false)
    }
  }

  // ── Navigation ─────────────────────────────────────────────────────────────
  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const handleNext = async () => {
    if (currentStep === 1 && !validateStep1()) return
    if (currentStep === 2 && !validateStep2()) return
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  // ── Checkout ───────────────────────────────────────────────────────────────
  const handleCheckout = async () => {
    setCheckingOut(true)
    setErrors({})
    try {
      // Save event as PENDING first (if not already saved)
      let eventId = pendingEventId
      if (!eventId) {
        const res = await submissionsApi.create({
          ...formData,
          price: formData.price ? parseFloat(formData.price) : undefined,
          organizer_id: user.id,
          organizer_email: user.email!,
          submission_type: 'paid',
        })
        eventId = res.data.id
        setPendingEventId(eventId)
      }

      const res = await checkoutApi.createSession({
        plan,
        featured: featuredChecked,
        event_id: eventId!,
      })
      // Redirect to Stripe — single checkout, single charge
      window.location.href = res.data.checkout_url
    } catch (err: any) {
      setErrors({ submit: err.response?.data?.detail || err.message || 'Could not start checkout. Please try again.' })
      setCheckingOut(false)
    }
  }

  // ── Display total ──────────────────────────────────────────────────────────
  const basePrice = plan === 'single' ? SINGLE_PRICE : UNLIMITED_PRICE
  const totalToday = basePrice + (featuredChecked ? FEATURED_PRICE : 0)
  const totalLabel =
    plan === 'single'
      ? `$${totalToday}`
      : featuredChecked
      ? `$${UNLIMITED_PRICE}/mo + $${FEATURED_PRICE} today`
      : `$${UNLIMITED_PRICE}/mo`

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-12 h-12 animate-spin text-primary-600" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Submit Your Event</h1>
          <p className="text-gray-600 mt-2">Get your event in front of Dallas' most engaged local audience</p>
        </div>

        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {STEPS.map((step, idx) => (
              <div key={step.id} className="flex-1">
                <div className="flex items-center">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                    currentStep > step.id ? 'bg-primary-600 border-primary-600'
                    : currentStep === step.id ? 'border-primary-600 text-primary-600'
                    : 'border-gray-300 text-gray-400'
                  }`}>
                    {currentStep > step.id ? <Check className="w-5 h-5 text-white" /> : <span className="font-semibold">{step.id}</span>}
                  </div>
                  {idx < STEPS.length - 1 && (
                    <div className={`flex-1 h-0.5 mx-4 ${currentStep > step.id ? 'bg-primary-600' : 'bg-gray-300'}`} />
                  )}
                </div>
                <div className="mt-2">
                  <p className={`text-sm font-medium ${currentStep >= step.id ? 'text-gray-900' : 'text-gray-400'}`}>{step.name}</p>
                  <p className="text-xs text-gray-500">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{STEPS[currentStep - 1].name}</CardTitle>
            <CardDescription>{STEPS[currentStep - 1].description}</CardDescription>
          </CardHeader>
          <CardContent>

            {/* ── Step 1: Event Details ─────────────────────────────────── */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <div>
                  <Label htmlFor="title">Event Title *</Label>
                  <Input id="title" placeholder="Summer Music Festival 2026" value={formData.title}
                    onChange={e => updateField('title', e.target.value)} className={errors.title ? 'border-red-500' : ''} />
                  {errors.title && <p className="text-sm text-red-600 mt-1">{errors.title}</p>}
                </div>
                <div>
                  <Label htmlFor="primary_url">Event Website / Tickets URL</Label>
                  <Input id="primary_url" type="url" placeholder="https://yourwebsite.com/event"
                    value={formData.primary_url} onChange={e => updateField('primary_url', e.target.value)} />
                  <p className="text-xs text-gray-500 mt-1">Where can people buy tickets or learn more?</p>
                </div>
                <div>
                  <Label htmlFor="format">Event Format *</Label>
                  <select id="format" value={formData.format} onChange={e => updateField('format', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-600">
                    <option value="in-person">In-Person</option>
                    <option value="online">Online / Virtual</option>
                    <option value="hybrid">Hybrid (In-Person + Online)</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="country">Country *</Label>
                  <Input id="country" value={formData.country} onChange={e => updateField('country', e.target.value)} />
                </div>
              </div>
            )}

            {/* ── Step 2: Date & Location ───────────────────────────────── */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="venue">Venue Name</Label>
                    <Input id="venue" placeholder="The Rustic" value={formData.venue}
                      onChange={e => updateField('venue', e.target.value)} />
                  </div>
                  <div>
                    <Label htmlFor="city">City *</Label>
                    <Input id="city" placeholder="Dallas" value={formData.city}
                      onChange={e => updateField('city', e.target.value)} className={errors.city ? 'border-red-500' : ''} />
                    {errors.city && <p className="text-sm text-red-600 mt-1">{errors.city}</p>}
                  </div>
                </div>
                <div>
                  <Label htmlFor="address">Street Address</Label>
                  <Input id="address" placeholder="123 Main Street" value={formData.address}
                    onChange={e => updateField('address', e.target.value)} />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="state">State</Label>
                    <Input id="state" placeholder="TX" value={formData.state} onChange={e => updateField('state', e.target.value)} />
                  </div>
                  <div>
                    <Label htmlFor="zip_code">ZIP Code</Label>
                    <Input id="zip_code" placeholder="75201" value={formData.zip_code} onChange={e => updateField('zip_code', e.target.value)} />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="start_date">Start Date & Time *</Label>
                    <Input id="start_date" type="datetime-local" value={formData.start_date}
                      onChange={e => updateField('start_date', e.target.value)} className={errors.start_date ? 'border-red-500' : ''} />
                    {errors.start_date && <p className="text-sm text-red-600 mt-1">{errors.start_date}</p>}
                  </div>
                  <div>
                    <Label htmlFor="end_date">End Date & Time (Optional)</Label>
                    <Input id="end_date" type="datetime-local" value={formData.end_date}
                      onChange={e => updateField('end_date', e.target.value)} />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="price_tier">Ticket Pricing</Label>
                    <select id="price_tier" value={formData.price_tier} onChange={e => updateField('price_tier', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-600">
                      <option value="free">Free</option>
                      <option value="paid">Paid</option>
                    </select>
                  </div>
                  {formData.price_tier === 'paid' && (
                    <div>
                      <Label htmlFor="price">Ticket Price ($)</Label>
                      <Input id="price" type="number" step="0.01" placeholder="25.00" value={formData.price}
                        onChange={e => updateField('price', e.target.value)} />
                    </div>
                  )}
                </div>
                <div>
                  <Label htmlFor="image">Event Image (Optional)</Label>
                  <div className="mt-2">
                    {imagePreview ? (
                      <div className="relative">
                        <img src={imagePreview} alt="Event preview" className="w-full h-48 object-cover rounded-lg" />
                        <button type="button" onClick={() => { setImagePreview(''); updateField('image_url', '') }}
                          className="absolute top-2 right-2 bg-red-500 text-white px-3 py-1 rounded-md text-sm hover:bg-red-600">
                          Remove
                        </button>
                      </div>
                    ) : (
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors">
                        <input type="file" id="image" accept="image/*" onChange={handleImageUpload} className="hidden" />
                        <label htmlFor="image" className="cursor-pointer flex flex-col items-center">
                          <svg className="w-12 h-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <p className="text-sm font-medium text-gray-700">Click to upload event image</p>
                          <p className="text-xs text-gray-500 mt-1">PNG, JPG up to 5MB</p>
                        </label>
                      </div>
                    )}
                    {uploading && <p className="text-sm text-blue-600 mt-2">Uploading image…</p>}
                    {errors.image && <p className="text-sm text-red-600 mt-2">{errors.image}</p>}
                  </div>
                </div>
                <div>
                  <Label htmlFor="description">Event Description *</Label>
                  <Textarea id="description" rows={6} placeholder="Tell people about your event…"
                    value={formData.description} onChange={e => updateField('description', e.target.value)}
                    className={errors.description ? 'border-red-500' : ''} />
                  {errors.description && <p className="text-sm text-red-600 mt-1">{errors.description}</p>}
                </div>
                <div>
                  <Label htmlFor="organizer_contact">Organizer Contact Email</Label>
                  <Input id="organizer_contact" type="email" value={formData.organizer_contact}
                    onChange={e => updateField('organizer_contact', e.target.value)} />
                </div>
              </div>
            )}

            {/* ── Step 3: Payment ───────────────────────────────────────── */}
            {currentStep === 3 && (
              <div className="space-y-8">

                {/* Plan selector */}
                <div>
                  <h3 className="text-lg font-semibold mb-1">Choose Your Plan</h3>
                  <p className="text-sm text-gray-500 mb-4">Get your event in front of thousands of Dallas locals. Every plan goes live instantly.</p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                    {/* Single event */}
                    <button type="button" onClick={() => setPlan('single')}
                      className={`p-5 border-2 rounded-lg text-left transition-all ${
                        plan === 'single' ? 'border-primary-600 bg-primary-50 shadow-md' : 'border-gray-200 hover:border-gray-300'
                      }`}>
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <p className="font-bold text-lg text-gray-900">Single Event</p>
                          <p className="text-2xl font-extrabold text-primary-700 mt-1">${SINGLE_PRICE}</p>
                          <p className="text-xs text-gray-500">one-time payment</p>
                        </div>
                        <div className={`w-5 h-5 mt-1 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                          plan === 'single' ? 'border-primary-600 bg-primary-600' : 'border-gray-300'}`}>
                          {plan === 'single' && <Check className="w-3 h-3 text-white" />}
                        </div>
                      </div>
                      <p className="text-xs text-gray-500 mb-3">Perfect for one-off events and first-time organizers.</p>
                      <ul className="space-y-1.5 text-sm text-gray-600">
                        <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-green-500 flex-shrink-0" /> Published on the calendar instantly</li>
                        <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-green-500 flex-shrink-0" /> Discoverable by date, city & category</li>
                        <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-green-500 flex-shrink-0" /> Direct link to your ticketing page</li>
                      </ul>
                    </button>

                    {/* Unlimited events */}
                    <button type="button" onClick={() => setPlan('unlimited')}
                      className={`p-5 border-2 rounded-lg text-left transition-all relative ${
                        plan === 'unlimited' ? 'border-primary-600 bg-primary-50 shadow-md' : 'border-gray-200 hover:border-gray-300'
                      }`}>
                      <div className="absolute -top-3 left-4 bg-primary-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-sm">
                        BEST FOR VENUES & PR
                      </div>
                      <div className="flex items-start justify-between mb-2 mt-2">
                        <div>
                          <p className="font-bold text-lg text-gray-900">Unlimited Events</p>
                          <p className="text-2xl font-extrabold text-primary-700 mt-1">${UNLIMITED_PRICE}<span className="text-sm font-normal text-gray-500">/mo</span></p>
                          <p className="text-xs text-gray-500">cancel anytime, no contracts</p>
                        </div>
                        <div className={`w-5 h-5 mt-1 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                          plan === 'unlimited' ? 'border-primary-600 bg-primary-600' : 'border-gray-300'}`}>
                          {plan === 'unlimited' && <Check className="w-3 h-3 text-white" />}
                        </div>
                      </div>
                      <p className="text-xs text-gray-500 mb-3">Ideal for venues, promoters & organizations with a full calendar.</p>
                      <ul className="space-y-1.5 text-sm text-gray-600">
                        <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-green-500 flex-shrink-0" /> Post as many events as you want</li>
                        <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-green-500 flex-shrink-0" /> Priority review & faster publishing</li>
                        <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-green-500 flex-shrink-0" /> Manage all events from one dashboard</li>
                        <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-green-500 flex-shrink-0" /> Saves 60%+ vs. individual posts</li>
                      </ul>
                    </button>

                  </div>
                </div>

                {/* Featured add-on */}
                <div>
                  <h3 className="text-lg font-semibold mb-1">Want more eyes on your event? <span className="text-amber-600">+${FEATURED_PRICE}</span></h3>
                  <p className="text-sm text-gray-500 mb-4">
                    Featured events get pinned to the top of the calendar — the very first thing
                    visitors see when they land on the page. One-time charge, active until your event date.
                  </p>

                  {/* Side-by-side preview with real event data */}
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    <div>
                      <p className="text-xs text-gray-400 font-medium mb-1.5 uppercase tracking-wide">Standard listing</p>
                      <EventPreviewCard
                        title={formData.title}
                        startDate={formData.start_date}
                        venue={formData.venue}
                        city={formData.city}
                      />
                    </div>
                    <div>
                      <p className="text-xs text-amber-600 font-medium mb-1.5 uppercase tracking-wide">Featured listing ★</p>
                      <EventPreviewCard
                        title={formData.title}
                        startDate={formData.start_date}
                        venue={formData.venue}
                        city={formData.city}
                        featured
                      />
                    </div>
                  </div>

                  {/* Featured checkbox */}
                  <label className={`flex items-center gap-3 p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    featuredChecked ? 'border-amber-400 bg-amber-50' : 'border-gray-200 hover:border-amber-300'
                  }`}>
                    <input
                      type="checkbox"
                      checked={featuredChecked}
                      onChange={e => setFeaturedChecked(e.target.checked)}
                      className="w-5 h-5 accent-amber-500"
                    />
                    <div>
                      <p className="font-semibold text-gray-900">Yes, feature my event — <span className="text-amber-700">+${FEATURED_PRICE}</span></p>
                      <p className="text-xs text-gray-500 mt-0.5">Pinned to top · Highlighted card · Featured badge · Maximum visibility</p>
                    </div>
                  </label>
                </div>

                {/* Live total */}
                <div className="border-t pt-6">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-gray-700">
                      {plan === 'single' ? 'Single event listing' : 'Unlimited events plan'}
                    </span>
                    <span className="font-medium">
                      {plan === 'single' ? `$${SINGLE_PRICE}` : `$${UNLIMITED_PRICE}/mo`}
                    </span>
                  </div>
                  {featuredChecked && (
                    <div className="flex items-center justify-between mb-1 text-amber-700">
                      <span>Featured placement</span>
                      <span className="font-medium">+${FEATURED_PRICE}</span>
                    </div>
                  )}
                  <div className="flex items-center justify-between border-t pt-3 mt-3">
                    <span className="font-bold text-gray-900 text-lg">Total today</span>
                    <span className="font-extrabold text-primary-700 text-xl">{totalLabel}</span>
                  </div>
                  {plan === 'unlimited' && (
                    <p className="text-xs text-gray-400 mt-1 text-right">Then ${UNLIMITED_PRICE}/mo. Cancel anytime — no questions asked.</p>
                  )}
                </div>

                {errors.submit && (
                  <div className="text-sm text-red-600 bg-red-50 border border-red-200 p-3 rounded-md">
                    {errors.submit}
                  </div>
                )}

              </div>
            )}

            {/* ── Navigation ─────────────────────────────────────────────── */}
            <div className="flex items-center justify-between mt-8 pt-6 border-t">
              <Button type="button" variant="outline" onClick={handleBack}
                disabled={currentStep === 1 || checkingOut}>
                <ChevronLeft className="w-4 h-4 mr-2" />
                Back
              </Button>

              {currentStep < 3 ? (
                <Button type="button" onClick={handleNext}>
                  Next <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button type="button" onClick={handleCheckout} disabled={checkingOut}
                  className="bg-primary-600 hover:bg-primary-700 text-white px-8">
                  {checkingOut ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Redirecting to payment…</>
                  ) : (
                    <>Pay {totalLabel} →</>
                  )}
                </Button>
              )}
            </div>

          </CardContent>
        </Card>
      </div>
    </div>
  )
}
