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
    // Set up path aliases
    config.resolve = config.resolve || {}
    
    // Set the @ alias - this is the key
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      '@': projectRoot,
    }
    
    // Use a webpack plugin to debug/resolve paths
    const webpack = require('webpack')
    
    // Add a plugin to log unresolved modules (for debugging)
    config.plugins = config.plugins || []
    config.plugins.push(
      new webpack.NormalModuleReplacementPlugin(/^@\/(.*)$/, (resource) => {
        const match = resource.request.match(/^@\/(.*)$/)
        if (match) {
          resource.request = path.resolve(projectRoot, match[1])
        }
      })
    )
    
    return config
  },
}

module.exports = nextConfig
