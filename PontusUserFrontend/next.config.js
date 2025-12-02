/** @type {import('next').NextConfig} */
const path = require('path')

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: [],
    unoptimized: false,
  },
  // Use webpack instead of Turbopack for better path alias support
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Get the absolute path to the project root
    const projectRoot = path.resolve(__dirname)
    
    // Debug: Log the project root (will show in build logs)
    console.log('Webpack config - Project root:', projectRoot)
    console.log('Webpack config - __dirname:', __dirname)
    
    // Resolve path aliases - ensure @ points to project root
    config.resolve = config.resolve || {}
    config.resolve.alias = config.resolve.alias || {}
    
    // Set the @ alias to the project root
    config.resolve.alias['@'] = projectRoot
    
    // Also try setting it with trailing slash
    config.resolve.alias['@/'] = path.join(projectRoot, '/')
    
    // Ensure proper module resolution
    config.resolve.modules = [
      path.resolve(projectRoot, 'node_modules'),
      ...(config.resolve.modules || ['node_modules']),
    ]
    
    // Ensure extensions are resolved
    config.resolve.extensions = [
      '.tsx',
      '.ts',
      '.jsx',
      '.js',
      '.json',
      ...(config.resolve.extensions || []),
    ]
    
    return config
  },
}

module.exports = nextConfig

