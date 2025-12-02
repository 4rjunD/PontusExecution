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
  webpack: (config, { isServer }) => {
    const webpack = require('webpack')
    
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
    
    // Use NormalModuleReplacementPlugin to handle @/ imports
    // This replaces @/lib/utils with the actual file path
    config.plugins = config.plugins || []
    config.plugins.push(
      new webpack.NormalModuleReplacementPlugin(
        /^@\//,
        (resource) => {
          // Replace @/ with project root path
          const newPath = resource.context.replace(/@\/$/, '')
          if (resource.request.startsWith('@/')) {
            const relativePath = resource.request.replace('@/', '')
            // Use context-relative resolution
            resource.request = path.resolve(projectRoot, relativePath)
          }
        }
      )
    )
    
    return config
  },
}

module.exports = nextConfig
