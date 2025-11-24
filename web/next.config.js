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
  // Don't use standalone mode - use custom server instead
  // output: 'standalone',
  // Skip build errors for now - pages will render dynamically at runtime
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  // Don't fail build on pre-render errors
  generateBuildId: async () => {
    return 'build-' + Date.now()
  },
}

module.exports = nextConfig
