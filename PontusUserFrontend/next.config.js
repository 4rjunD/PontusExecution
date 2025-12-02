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
  webpack: (config) => {
    // Set up resolve with alias
    config.resolve = config.resolve || {}
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      '@': projectRoot,
    }
    
    // Ensure extensions
    config.resolve.extensions = [
      '.tsx',
      '.ts',
      '.jsx',
      '.js',
      '.json',
      ...(config.resolve.extensions || []),
    ]
    
    // Ensure modules includes project node_modules
    config.resolve.modules = [
      path.join(projectRoot, 'node_modules'),
      ...(config.resolve.modules || []).filter(m => 
        typeof m === 'string' && !m.includes('node_modules')
      ),
      'node_modules',
    ]
    
    return config
  },
}

module.exports = nextConfig
