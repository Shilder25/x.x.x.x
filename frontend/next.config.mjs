/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // Only use localhost rewrites in development (Replit)
    // In production (Railway), frontend uses NEXT_PUBLIC_API_URL directly
    if (process.env.NEXT_PUBLIC_API_URL) {
      // Production mode - no rewrites needed
      return [];
    }
    
    // Development mode - rewrite to local Flask backend
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
