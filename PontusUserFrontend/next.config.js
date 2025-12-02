/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: [],
    unoptimized: false,
  },
  // Use webpack instead of Turbopack for better path alias support
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Get the absolute path to the project root
    const projectRoot = path.resolve(__dirname)
    
    // Resolve path aliases - ensure @ points to project root
    if (!config.resolve.alias) {
      config.resolve.alias = {}
    }
    config.resolve.alias['@'] = projectRoot
    
    // Ensure proper module resolution
    if (!config.resolve.modules) {
      config.resolve.modules = []
    }
    config.resolve.modules = [
      path.resolve(projectRoot, 'node_modules'),
      ...config.resolve.modules,
    ]
    
    return config
  },
}

module.exports = nextConfig

