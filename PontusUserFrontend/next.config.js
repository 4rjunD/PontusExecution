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
  // Use webpack instead of Turbopack
  webpack: (config, { isServer }) => {
    // CRITICAL: Set alias BEFORE any other resolution
    config.resolve = config.resolve || {}
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      '@': projectRoot,
    }
    
    // Ensure proper module resolution order
    config.resolve.modules = [
      path.resolve(projectRoot, 'node_modules'),
      ...(config.resolve.modules || []).filter(m => 
        typeof m === 'string' && !m.includes('node_modules')
      ),
      'node_modules',
    ]
    
    // Add extensions if not present
    if (!config.resolve.extensions) {
      config.resolve.extensions = []
    }
    const extensions = ['.tsx', '.ts', '.jsx', '.js', '.json']
    extensions.forEach(ext => {
      if (!config.resolve.extensions.includes(ext)) {
        config.resolve.extensions.push(ext)
      }
    })
    
    return config
  },
}

module.exports = nextConfig
