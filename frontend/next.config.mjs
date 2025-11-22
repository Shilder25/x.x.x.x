/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // Disable rewrites when NEXT_PUBLIC_API_URL is set (Railway multi-service deployment)
    // This variable must be set as a build-time environment variable in Railway
    if (process.env.NEXT_PUBLIC_API_URL) {
      console.log('[Next.js Config] Railway mode detected - using NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
      return [];
    }
    
    // Replit or local development - rewrite to local Flask backend
    console.log('[Next.js Config] Development mode - using localhost:8000 rewrites');
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
