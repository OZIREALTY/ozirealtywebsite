// Serves the live site's clean URLs (/about-adelaide-land-agent, /post/<slug>, /blog/categories/<c>)
// from the generated static files (public/<path>.html) without changing the address.
import type { APIRoute } from 'astro';

export const prerender = false;

async function asset(url: URL) {
  const res = await fetch(url, { headers: { 'x-ozi-internal': '1' } });
  return res.ok ? res : null;
}

export const GET: APIRoute = async ({ params, request }) => {
  const slug = (params.slug ?? '').replace(/\/+$/, '');
  const base = new URL(request.url);
  if (slug && !slug.includes('.') && !request.headers.get('x-ozi-internal')) {
    const page = await asset(new URL(`/${slug}.html`, base));
    if (page) {
      return new Response(page.body, {
        status: 200,
        headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'public, max-age=300' },
      });
    }
  }
  const notFound = await asset(new URL('/404.html', base));
  return new Response(notFound ? notFound.body : 'Not found', {
    status: 404,
    headers: { 'content-type': 'text/html; charset=utf-8' },
  });
};
