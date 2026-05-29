import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export function formatDateTime(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'pending':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'approved':
    case 'published':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'rejected':
      return 'text-red-600 bg-red-50 border-red-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

export function getStatusLabel(status: string): string {
  switch (status) {
    case 'pending':
      return 'Under Review'
    case 'approved':
      return 'Approved'
    case 'published':
      return 'Published'
    case 'rejected':
      return 'Rejected'
    default:
      return status
  }
}

// Exact slug formula from fid-main lib/events/slug.ts — must stay in sync
function slugifyTitle(title: string): string {
  return title
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 80)
}

export function buildFidMainEventUrl(event: { id: number; title: string }): string {
  return `https://firstindallas.com/events/${slugifyTitle(event.title)}-${event.id}/`
}
