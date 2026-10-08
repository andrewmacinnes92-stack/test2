# Going live on independentclaimsconsultants.com

The site is built for `https://independentclaimsconsultants.com` (no `www`), which matches the main address the current WordPress site gives Google. If you choose `www` instead, change `SITE` in `_build/build.py` and rebuild.

## 1. Before switching

- Pick a host. Netlify or Cloudflare Pages (both free) read the `_redirects` file and send proper permanent (301) redirects for the old addresses. GitHub Pages can host the site too, using the HTML redirect pages that are generated as a fallback.
- Rebuild: `python3 _build/build.py`

## 2. On the day

- Point the domain at the new host and turn on HTTPS.
- Make the other versions of the address (`http://`, `www.`) redirect to `https://independentclaimsconsultants.com`. This is a setting in the host's domain options.
- Check that these old addresses land on the right new pages:
  - `/about/` → `/about/`
  - `/faq/` → `/faq/`
  - `/contact/` → `/contact/`
  - `/contact-2/` → `/contact/`
  - `/commercial-claims/` → `/claims/#businesses`
  - `/domestic-insurance-claim/` → `/claims/#homeowners`
  - `/sample-page/`, `/services2/`, `/services3/` and `/call-0161-768765/` → homepage

## 3. Straight after

- Google Search Console: verify the domain, submit `https://independentclaimsconsultants.com/sitemap.xml`, and use URL Inspection to request indexing of the homepage and the Surrey page.
- Bing Webmaster Tools: import from Search Console and submit the same sitemap.
- Test a page in Google's Rich Results Test (business details, FAQs, breadcrumbs).
- Share a page link in WhatsApp or LinkedIn to check the preview image appears.

## Pages and files the build creates

| Address | Purpose |
| --- | --- |
| `/` | Homepage |
| `/claims/` | Claims we handle |
| `/about/` | About us and team |
| `/advice/` | Advice centre |
| `/faq/` | FAQs |
| `/contact/` | Start your claim |
| `/loss-assessors-surrey/` | Southern office (Cobham) location page |
| `/loss-assessors-elmbridge/`, `/loss-assessors-guildford/`, `/loss-assessors-woking/`, `/loss-assessors-epsom-leatherhead/`, `/loss-assessors-london/` | Local area pages for the Southern office |
| `/loss-assessors-manchester/` | Head office (Hale) location page |
| `/404.html` | Page not found |
| `/sitemap.xml`, `/robots.txt` | For search engines |
| `/_redirects` | Permanent redirects (Netlify / Cloudflare Pages) |
