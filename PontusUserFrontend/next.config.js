/** @type {import('next').NextConfig} */
const path = require('path')

// Get absolute path to project root
const projectRoot = path.resolve(__dirname || process.cwd())

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: [],
    unoptimized: false,
  },
  // Use webpack instead of Turbopack for better path alias support
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Initialize resolve if it doesn't exist
    if (!config.resolve) {
      config.resolve = {}
    }
    
    // Initialize alias object
    if (!config.resolve.alias) {
      config.resolve.alias = {}
    }
    
    // CRITICAL: Set alias as an object with exact match
    // Webpack needs this format for proper resolution
    const aliases = {
      '@': projectRoot,
    }
    
    // Merge with existing aliases, but ensure ours take precedence
    config.resolve.alias = {
      ...config.resolve.alias,
      ...aliases,
    }
    
    // Also ensure symlinks are resolved
    config.resolve.symlinks = false
    
    // Set modules resolution
    config.resolve.modules = [
      path.join(projectRoot, 'node_modules'),
      ...(config.resolve.modules || []).filter(m => !m.includes('node_modules')),
      'node_modules',
    ]
    
    return config
  },
}

module.exports = nextConfig
