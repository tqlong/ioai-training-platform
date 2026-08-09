const apiBase = (process.env.API_INTERNAL_BASE ?? 'http://127.0.0.1:8000').replace(/\/$/, '');

/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${apiBase}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
