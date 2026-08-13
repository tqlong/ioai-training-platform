import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const publicNotFound = {
  error: {
    code: 'PUBLIC_NOT_FOUND',
    message: 'Resource not found.',
  },
};

export function middleware(request: NextRequest): NextResponse {
  const path = request.nextUrl.pathname;
  if (path === '/api/v1/author' || path.startsWith('/api/v1/author/')) {
    return NextResponse.json(publicNotFound, { status: 404 });
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/api/v1/author/:path*'],
};
