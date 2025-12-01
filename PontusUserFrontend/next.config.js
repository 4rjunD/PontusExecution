/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: [],
    unoptimized: false,
  },
  // Turbopack is enabled by default in Next.js 16
  // Path aliases are handled by tsconfig.json
  turbopack: {},
}

module.exports = nextConfig

