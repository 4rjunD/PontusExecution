/** @type {import('next').NextConfig} */
const path = require('path')
const fs = require('fs')

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
    
    // Use NormalModuleReplacementPlugin with proper file resolution
    config.plugins = config.plugins || []
    config.plugins.push(
      new webpack.NormalModuleReplacementPlugin(
        /^@\/(.*)$/,
        (resource) => {
          const match = resource.request.match(/^@\/(.*)$/)
          if (match) {
            const filePath = match[1]
            const basePath = path.resolve(projectRoot, filePath)
            
            // Try to find the actual file with extension
            const extensions = ['.ts', '.tsx', '.js', '.jsx', '.json']
            let foundPath = null
            
            // If path already has extension, check if it exists
            if (path.extname(filePath)) {
              if (fs.existsSync(basePath)) {
                foundPath = basePath
              }
            } else {
              // Try each extension
              for (const ext of extensions) {
                const testPath = basePath + ext
                if (fs.existsSync(testPath)) {
                  foundPath = testPath
                  break
                }
              }
            }
            
            // Replace the request with the found path
            if (foundPath) {
              resource.request = foundPath
            } else {
              // Fallback to base path (webpack will try extensions)
              resource.request = basePath
            }
          }
        }
      )
    )
    
    return config
  },
}

module.exports = nextConfig
