/** @type {import('next').NextConfig} */
const path = require('path')

// Get absolute path to project root
const projectRoot = path.resolve(__dirname)

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: [],
    unoptimized: false,
  },
  // Use webpack instead of Turbopack for better path alias support
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Ensure resolve object exists
    config.resolve = config.resolve || {}
    config.resolve.alias = config.resolve.alias || {}
    
    // Set @ alias to project root - this is critical
    config.resolve.alias['@'] = projectRoot
    
    // Ensure modules array exists and includes project node_modules first
    const existingModules = config.resolve.modules || ['node_modules']
    config.resolve.modules = [
      path.join(projectRoot, 'node_modules'),
      ...existingModules.filter(m => m !== 'node_modules'),
      'node_modules',
    ]
    
    return config
  },
}

module.exports = nextConfig

