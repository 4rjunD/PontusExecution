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
    
    // Use a webpack plugin to resolve @ paths with proper extensions
    const webpack = require('webpack')
    
    config.plugins = config.plugins || []
    config.plugins.push(
      new webpack.NormalModuleReplacementPlugin(/^@\/(.*)$/, (resource) => {
        const match = resource.request.match(/^@\/(.*)$/)
        if (match) {
          const filePath = match[1]
          const resolvedPath = path.resolve(projectRoot, filePath)
          
          // Try to resolve with extensions if no extension provided
          const fs = require('fs')
          const extensions = ['.ts', '.tsx', '.js', '.jsx', '.json']
          
          // If path already has extension, use it directly
          if (path.extname(filePath)) {
            resource.request = resolvedPath
          } else {
            // Try to find file with extension
            let found = false
            for (const ext of extensions) {
              const fullPath = resolvedPath + ext
              if (fs.existsSync(fullPath)) {
                resource.request = fullPath
                found = true
                break
              }
            }
            if (!found) {
              resource.request = resolvedPath
            }
          }
        }
      })
    )
    
    return config
  },
}

module.exports = nextConfig
