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
    // Get existing aliases (Next.js might have some)
    const existingAliases = config.resolve?.alias || {}
    
    // Override with our aliases - must come AFTER existing ones are read
    config.resolve = config.resolve || {}
    config.resolve.alias = {
      ...existingAliases,
      '@': projectRoot,
      '@/lib': path.join(projectRoot, 'lib'),
      '@/components': path.join(projectRoot, 'components'),
      '@/app': path.join(projectRoot, 'app'),
    }
    
    // Ensure proper module resolution
    if (!config.resolve.modules) {
      config.resolve.modules = []
    }
    if (!config.resolve.modules.includes(path.join(projectRoot, 'node_modules'))) {
      config.resolve.modules.unshift(path.join(projectRoot, 'node_modules'))
    }
    
    return config
  },
}

module.exports = nextConfig
