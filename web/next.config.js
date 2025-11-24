/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['images.unsplash.com', 'localhost'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  // Disable static optimization for dashboard pages that require auth
  experimental: {
    missingSuspenseWithCSRBailout: false,
  },
  // Allow dynamic routes
  output: 'standalone',
}

module.exports = nextConfig
