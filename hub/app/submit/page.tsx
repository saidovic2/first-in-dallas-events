'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { submissionsApi } from '@/lib/api'
import { Nav } from '@/components/layout/nav'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Check, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react'

const STEPS = [
  { id: 1, name: 'Edit Event', description: 'Basic event information' },
  { id: 2, name: 'Review', description: 'Location, date & details' },
  { id: 3, name: 'Promotion Options', description: 'Choose submission type' },
]

export default function SubmitPage() {
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(1)
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const [formData, setFormData] = useState({
    // Step 1: Edit Event
    title: '',
    primary_url: '',
    format: 'in-person' as 'in-person' | 'online' | 'hybrid',
    country: 'USA',
    
    // Step 2: Review
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
    
    // Step 3: Promotion
    submission_type: 'free' as 'free' | 'paid',
  })

  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string>('')
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    checkUser()
  }, [])

  const checkUser = async () => {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      router.push('/auth/login')
      return
    }
    setUser(user)
    setFormData(prev => ({ ...prev, organizer_contact: user.email! }))
  }

  const updateField = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validateStep1 = () => {
    const newErrors: Record<string, string> = {}
    if (!formData.title.trim()) newErrors.title = 'Event title is required'
    if (!formData.format) newErrors.format = 'Event format is required'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const validateStep2 = () => {
    const newErrors: Record<string, string> = {}
    if (!formData.city.trim()) newErrors.city = 'City is required'
    if (!formData.start_date) newErrors.start_date = 'Start date is required'
    if (!formData.description.trim()) newErrors.description = 'Description is required'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setErrors({ ...errors, image: 'Please upload an image file' })
      return
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrors({ ...errors, image: 'Image must be less than 5MB' })
      return
    }

    setImageFile(file)
    
    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setImagePreview(reader.result as string)
    }
    reader.readAsDataURL(file)

    // Upload to Supabase Storage
    setUploading(true)
    try {
      const fileExt = file.name.split('.').pop()
      const fileName = `${user.id}-${Date.now()}.${fileExt}`
      const filePath = `event-images/${fileName}`

      const { error: uploadError } = await supabase.storage
        .from('events')
        .upload(filePath, file)

      if (uploadError) throw uploadError

      // Get public URL
      const { data } = supabase.storage
        .from('events')
        .getPublicUrl(filePath)

      updateField('image_url', data.publicUrl)
    } catch (error: any) {
      console.error('Upload error:', error)
      setErrors({ ...errors, image: 'Failed to upload image. You can continue without an image.' })
    } finally {
      setUploading(false)
    }
  }

  const handleNext = () => {
    if (currentStep === 1 && !validateStep1()) return
    if (currentStep === 2 && !validateStep2()) return
    
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      // Prepare submission data with proper date formatting
      const submissionData: any = {
        organizer_id: user.id,
        title: formData.title,
        primary_url: formData.primary_url || null,
        format: formData.format,
        country: formData.country,
        venue: formData.venue || null,
        address: formData.address || null,
        city: formData.city,
        state: formData.state || null,
        zip_code: formData.zip_code || null,
        start_date: formData.start_date ? new Date(formData.start_date).toISOString() : null,
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null,
        price: formData.price ? parseFloat(formData.price) : null,
        price_tier: formData.price_tier,
        image_url: formData.image_url || null,
        description: formData.description,
        organizer_contact: formData.organizer_contact,
        submission_type: formData.submission_type,
      }

      // Create submission in Supabase
      const { data: submission, error: supabaseError } = await supabase
        .from('event_submissions')
        .insert(submissionData)
        .select()
        .single()

      if (supabaseError) throw supabaseError

      // Sync to CMS API
      try {
        await submissionsApi.create({
          ...formData,
          price: formData.price ? parseFloat(formData.price) : undefined,
          organizer_id: user.id,
          organizer_email: user.email!,
        })
      } catch (apiError) {
        console.error('CMS API sync error:', apiError)
        // Continue even if API sync fails
      }

      // Show success and redirect
      router.push('/submissions?success=true')
    } catch (error: any) {
      console.error('Submission error:', error)
      setErrors({ submit: error.message || 'Failed to submit event' })
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Submit New Event</h1>
          <p className="text-gray-600 mt-2">Share your event with the First in Dallas community</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {STEPS.map((step, idx) => (
              <div key={step.id} className="flex-1">
                <div className="flex items-center">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                    currentStep > step.id
                      ? 'bg-primary-600 border-primary-600'
                      : currentStep === step.id
                      ? 'border-primary-600 text-primary-600'
                      : 'border-gray-300 text-gray-400'
                  }`}>
                    {currentStep > step.id ? (
                      <Check className="w-5 h-5 text-white" />
                    ) : (
                      <span className="font-semibold">{step.id}</span>
                    )}
                  </div>
                  {idx < STEPS.length - 1 && (
                    <div className={`flex-1 h-0.5 mx-4 ${
                      currentStep > step.id ? 'bg-primary-600' : 'bg-gray-300'
                    }`} />
                  )}
                </div>
                <div className="mt-2">
                  <p className={`text-sm font-medium ${
                    currentStep >= step.id ? 'text-gray-900' : 'text-gray-400'
                  }`}>
                    {step.name}
                  </p>
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
            {/* Step 1: Edit Event */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <div>
                  <Label htmlFor="title">Event Title *</Label>
                  <Input
                    id="title"
                    placeholder="Summer Music Festival 2025"
                    value={formData.title}
                    onChange={(e) => updateField('title', e.target.value)}
                    className={errors.title ? 'border-red-500' : ''}
                  />
                  {errors.title && <p className="text-sm text-red-600 mt-1">{errors.title}</p>}
                </div>

                <div>
                  <Label htmlFor="primary_url">Event Website/URL</Label>
                  <Input
                    id="primary_url"
                    type="url"
                    placeholder="https://yourwebsite.com/event"
                    value={formData.primary_url}
                    onChange={(e) => updateField('primary_url', e.target.value)}
                  />
                  <p className="text-xs text-gray-500 mt-1">Where can people learn more or buy tickets?</p>
                </div>

                <div>
                  <Label htmlFor="format">Event Format *</Label>
                  <select
                    id="format"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-600"
                    value={formData.format}
                    onChange={(e) => updateField('format', e.target.value)}
                  >
                    <option value="in-person">In-Person</option>
                    <option value="online">Online/Virtual</option>
                    <option value="hybrid">Hybrid (In-Person + Online)</option>
                  </select>
                </div>

                <div>
                  <Label htmlFor="country">Country *</Label>
                  <Input
                    id="country"
                    value={formData.country}
                    onChange={(e) => updateField('country', e.target.value)}
                  />
                </div>
              </div>
            )}

            {/* Step 2: Review */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="venue">Venue Name</Label>
                    <Input
                      id="venue"
                      placeholder="The Rustic"
                      value={formData.venue}
                      onChange={(e) => updateField('venue', e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="city">City *</Label>
                    <Input
                      id="city"
                      placeholder="Dallas"
                      value={formData.city}
                      onChange={(e) => updateField('city', e.target.value)}
                      className={errors.city ? 'border-red-500' : ''}
                    />
                    {errors.city && <p className="text-sm text-red-600 mt-1">{errors.city}</p>}
                  </div>
                </div>

                <div>
                  <Label htmlFor="address">Street Address</Label>
                  <Input
                    id="address"
                    placeholder="123 Main Street"
                    value={formData.address}
                    onChange={(e) => updateField('address', e.target.value)}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="state">State</Label>
                    <Input
                      id="state"
                      placeholder="TX"
                      value={formData.state}
                      onChange={(e) => updateField('state', e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="zip_code">ZIP Code</Label>
                    <Input
                      id="zip_code"
                      placeholder="75201"
                      value={formData.zip_code}
                      onChange={(e) => updateField('zip_code', e.target.value)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="start_date">Start Date & Time *</Label>
                    <Input
                      id="start_date"
                      type="datetime-local"
                      value={formData.start_date}
                      onChange={(e) => updateField('start_date', e.target.value)}
                      className={errors.start_date ? 'border-red-500' : ''}
                    />
                    {errors.start_date && <p className="text-sm text-red-600 mt-1">{errors.start_date}</p>}
                  </div>
                  <div>
                    <Label htmlFor="end_date">End Date & Time (Optional)</Label>
                    <Input
                      id="end_date"
                      type="datetime-local"
                      value={formData.end_date}
                      onChange={(e) => updateField('end_date', e.target.value)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="price_tier">Price Tier</Label>
                    <select
                      id="price_tier"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-600"
                      value={formData.price_tier}
                      onChange={(e) => updateField('price_tier', e.target.value)}
                    >
                      <option value="free">Free</option>
                      <option value="paid">Paid</option>
                    </select>
                  </div>
                  {formData.price_tier === 'paid' && (
                    <div>
                      <Label htmlFor="price">Ticket Price ($)</Label>
                      <Input
                        id="price"
                        type="number"
                        step="0.01"
                        placeholder="25.00"
                        value={formData.price}
                        onChange={(e) => updateField('price', e.target.value)}
                      />
                    </div>
                  )}
                </div>

                <div>
                  <Label htmlFor="image">Event Image (Optional)</Label>
                  <div className="mt-2">
                    {imagePreview ? (
                      <div className="relative">
                        <img
                          src={imagePreview}
                          alt="Event preview"
                          className="w-full h-48 object-cover rounded-lg"
                        />
                        <button
                          type="button"
                          onClick={() => {
                            setImageFile(null)
                            setImagePreview('')
                            updateField('image_url', '')
                          }}
                          className="absolute top-2 right-2 bg-red-500 text-white px-3 py-1 rounded-md text-sm hover:bg-red-600"
                        >
                          Remove
                        </button>
                      </div>
                    ) : (
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors">
                        <input
                          type="file"
                          id="image"
                          accept="image/*"
                          onChange={handleImageUpload}
                          className="hidden"
                        />
                        <label htmlFor="image" className="cursor-pointer">
                          <div className="flex flex-col items-center">
                            <svg className="w-12 h-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <p className="text-sm font-medium text-gray-700">Click to upload event image</p>
                            <p className="text-xs text-gray-500 mt-1">PNG, JPG up to 5MB</p>
                          </div>
                        </label>
                      </div>
                    )}
                    {uploading && <p className="text-sm text-blue-600 mt-2">Uploading image...</p>}
                    {errors.image && <p className="text-sm text-red-600 mt-2">{errors.image}</p>}
                  </div>
                </div>

                <div>
                  <Label htmlFor="description">Event Description *</Label>
                  <Textarea
                    id="description"
                    rows={6}
                    placeholder="Tell people about your event..."
                    value={formData.description}
                    onChange={(e) => updateField('description', e.target.value)}
                    className={errors.description ? 'border-red-500' : ''}
                  />
                  {errors.description && <p className="text-sm text-red-600 mt-1">{errors.description}</p>}
                </div>

                <div>
                  <Label htmlFor="organizer_contact">Organizer Contact Email</Label>
                  <Input
                    id="organizer_contact"
                    type="email"
                    value={formData.organizer_contact}
                    onChange={(e) => updateField('organizer_contact', e.target.value)}
                  />
                </div>
              </div>
            )}

            {/* Step 3: Promotion Options */}
            {currentStep === 3 && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Choose Your Submission Type</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Free Option */}
                    <button
                      type="button"
                      onClick={() => updateField('submission_type', 'free')}
                      className={`p-6 border-2 rounded-lg text-left transition-all ${
                        formData.submission_type === 'free'
                          ? 'border-primary-600 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-lg">Free Submission</h4>
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                          formData.submission_type === 'free'
                            ? 'border-primary-600 bg-primary-600'
                            : 'border-gray-300'
                        }`}>
                          {formData.submission_type === 'free' && (
                            <Check className="w-4 h-4 text-white" />
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">Standard event listing</p>
                      <ul className="space-y-2 text-sm text-gray-600">
                        <li className="flex items-start">
                          <Check className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span>Listed on main calendar</span>
                        </li>
                        <li className="flex items-start">
                          <Check className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span>Searchable by date, city, and category</span>
                        </li>
                        <li className="flex items-start">
                          <Check className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span>Standard visibility</span>
                        </li>
                      </ul>
                    </button>

                    {/* Paid Option */}
                    <button
                      type="button"
                      onClick={() => updateField('submission_type', 'paid')}
                      className={`p-6 border-2 rounded-lg text-left transition-all relative overflow-hidden ${
                        formData.submission_type === 'paid'
                          ? 'border-amber-500 bg-gradient-to-br from-amber-50 to-yellow-50 shadow-lg'
                          : 'border-gray-200 hover:border-amber-300 hover:shadow-md'
                      }`}
                    >
                      <div className="absolute top-0 right-0">
                        <div className="bg-amber-500 text-white text-xs font-bold px-3 py-1 transform rotate-12 translate-x-2 -translate-y-1">
                          FEATURED
                        </div>
                      </div>
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-bold text-lg text-amber-900">🟧 Premium Featured</h4>
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                          formData.submission_type === 'paid'
                            ? 'border-amber-600 bg-amber-600'
                            : 'border-gray-300'
                        }`}>
                          {formData.submission_type === 'paid' && (
                            <Check className="w-4 h-4 text-white" />
                          )}
                        </div>
                      </div>
                      <p className="text-sm font-medium text-gray-700 mb-3">
                        Maximum exposure across Dallas' most engaged local audience
                      </p>
                      
                      {/* Reach Statistics */}
                      <div className="bg-white/60 rounded-lg p-3 mb-4">
                        <p className="text-sm font-semibold text-amber-800 text-center">
                          25,000+ newsletter readers · 15,000+ monthly site visitors
                        </p>
                      </div>

                      <div className="mb-3">
                        <p className="text-sm font-bold text-amber-900 mb-2">⭐ Includes:</p>
                      </div>

                      <ul className="space-y-2.5 text-sm text-gray-700 mb-4">
                        <li className="flex items-start">
                          <span className="text-amber-600 mr-2 mt-0.5">•</span>
                          <span><strong>Homepage Feature Sidebar</strong> — Prime placement on our most visited page</span>
                        </li>
                        <li className="flex items-start">
                          <span className="text-amber-600 mr-2 mt-0.5">•</span>
                          <span><strong>Daily Newsletter Shout-Out</strong> — Your event featured directly in our 25K-subscriber Dallas newsletter</span>
                        </li>
                        <li className="flex items-start">
                          <span className="text-amber-600 mr-2 mt-0.5">•</span>
                          <span><strong>Priority Search Placement</strong> — Listed at the top of event search results for maximum visibility</span>
                        </li>
                        <li className="flex items-start">
                          <span className="text-amber-600 mr-2 mt-0.5">•</span>
                          <span><strong>Extended Visibility</strong> — Featured for 30 days across the calendar and homepage</span>
                        </li>
                        <li className="flex items-start">
                          <span className="text-amber-600 mr-2 mt-0.5">•</span>
                          <span><strong>"Featured Event" Badge</strong> — Highlighted with a premium tag to stand out</span>
                        </li>
                      </ul>

                      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-3">
                        <p className="text-xs text-gray-700">
                          💡 <strong>Perfect for:</strong> concerts, restaurant openings, festivals, charity events, or any experience that deserves the spotlight.
                        </p>
                      </div>

                      <div className="pt-3 border-t border-amber-200">
                        <p className="text-xs text-amber-700 font-medium">
                          💰 Investment starts at $99 — our team will reach out to finalize placement and details.
                        </p>
                      </div>
                    </button>
                  </div>
                </div>

                {errors.submit && (
                  <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md">
                    {errors.submit}
                  </div>
                )}
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex items-center justify-between mt-8 pt-6 border-t">
              <Button
                type="button"
                variant="outline"
                onClick={handleBack}
                disabled={currentStep === 1 || loading}
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Back
              </Button>

              {currentStep < 3 ? (
                <Button type="button" onClick={handleNext}>
                  Next
                  <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button
                  type="button"
                  onClick={handleSubmit}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    'Submit Event'
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
