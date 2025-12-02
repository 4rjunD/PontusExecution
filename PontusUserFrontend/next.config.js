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
    
    // Ensure extensions are configured for TypeScript/JavaScript
    config.resolve.extensions = [
      '.tsx',
      '.ts',
      '.jsx',
      '.js',
      '.json',
      ...(config.resolve.extensions || []).filter(ext => 
        !['.tsx', '.ts', '.jsx', '.js', '.json'].includes(ext)
      ),
    ]
    
    // Use a webpack plugin to resolve @ paths
    const webpack = require('webpack')
    
    config.plugins = config.plugins || []
    config.plugins.push(
      new webpack.NormalModuleReplacementPlugin(/^@\/(.*)$/, (resource) => {
        const match = resource.request.match(/^@\/(.*)$/)
        if (match) {
          // Just replace @ with project root - webpack will handle extensions
          resource.request = path.resolve(projectRoot, match[1])
        }
      })
    )
    
    return config
  },
}

module.exports = nextConfig
