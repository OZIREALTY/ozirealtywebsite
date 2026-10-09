// Wix-managed headless project serving the generated Ozi Realty pages (../site) at the
// live site's original URLs, e.g. /about-adelaide-land-agent and /post/<slug>.
import { defineConfig } from 'astro/config';
import wix from '@wix/astro';
import wixPages from '@wix/astro-pages';
import react from '@astrojs/react';
import wixHostingAdapter from '@wix/astro-wix-hosting-adapter';

export default defineConfig({
  output: 'server',
  adapter: wixHostingAdapter(),
  integrations: [wix(), wixPages(), react()],
  image: { domains: ['static.wixstatic.com'] },
  security: { checkOrigin: false },
  trailingSlash: 'ignore',
  build: { format: 'directory' },
});
