/** @type {import('next').NextConfig} */
const path = require('path')

// Get absolute path to project root - use process.cwd() as fallback
const projectRoot = path.resolve(__dirname || process.cwd())

console.log('Next.js config loaded')
console.log('Project root:', projectRoot)
console.log('__dirname:', __dirname)
console.log('process.cwd():', process.cwd())

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: [],
    unoptimized: false,
  },
  // Use webpack instead of Turbopack for better path alias support
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    console.log('Webpack config executing...')
    console.log('Webpack - Project root:', projectRoot)
    console.log('Webpack - isServer:', isServer)
    
    // Ensure resolve object exists
    config.resolve = config.resolve || {}
    config.resolve.alias = config.resolve.alias || {}
    
    // Set @ alias to project root - this is critical
    config.resolve.alias['@'] = projectRoot
    console.log('Webpack - @ alias set to:', config.resolve.alias['@'])
    
    // Also set specific paths
    config.resolve.alias['@/lib'] = path.join(projectRoot, 'lib')
    config.resolve.alias['@/components'] = path.join(projectRoot, 'components')
    config.resolve.alias['@/app'] = path.join(projectRoot, 'app')
    
    // Ensure modules array exists and includes project node_modules first
    const existingModules = config.resolve.modules || ['node_modules']
    config.resolve.modules = [
      path.join(projectRoot, 'node_modules'),
      ...existingModules.filter(m => m !== 'node_modules'),
      'node_modules',
    ]
    
    console.log('Webpack config complete')
    return config
  },
}

module.exports = nextConfig
