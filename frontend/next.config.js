/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'assets-global.website-files.com',
      },
      {
        protocol: 'https',
        hostname: 'replit.com',
      },
      {
        protocol: 'https',
        hostname: 'seeklogo.com',
      },
    ],
  },
}

module.exports = nextConfig 