# Website analytics

The site supports two analytics tools. Each one switches on when its code is added to the top of `_build/build.py`.

| Setting | Tool | Cookies | Notes |
| --- | --- | --- | --- |
| `CF_ANALYTICS_TOKEN` | Cloudflare Web Analytics | None | Counts every visitor. No cookie banner needed. |
| `GA_MEASUREMENT_ID` | Google Analytics 4 | Yes | Only loads after a visitor clicks **Accept** on the cookie banner. The banner appears automatically once this is set. |

After changing either setting, run `python3 _build/package.py`, then upload and extract the new zip into `public_html`, overwriting the old files.

## Cloudflare Web Analytics (about 5 minutes)

1. Go to https://dash.cloudflare.com/sign-up and create a free account.
2. In the dashboard menu, open **Analytics & Logs** and then **Web Analytics**. Click **Add a site**.
3. Enter `independentclaimsconsultants.com` and choose the option to **add a JavaScript snippet manually**. You don't need to move the domain to Cloudflare.
4. Cloudflare shows a snippet containing `"token": "…"`. Copy the token, the long string of letters and numbers.

## Google Analytics 4 (about 10 minutes)

1. Go to https://analytics.google.com and sign in with the Google account the business should own.
2. Click **Start measuring**:
   - Account name: Independent Claims Consultants
   - Property name: independentclaimsconsultants.com
   - Time zone: United Kingdom
   - Currency: British pound
3. Choose **Web** as the platform. Enter `https://independentclaimsconsultants.com` and the stream name "Website".
4. Copy the **Measurement ID**. It starts with `G-`.
5. Optional, but useful: in **Admin**, then **Product links**, then **Search Console links**, link the site's Search Console property. Google search data will then appear in Analytics too.

## Where to see the numbers

- **Cloudflare:** dash.cloudflare.com, then **Web Analytics**. Shows visits, page views, top pages, referrers, countries and devices.
- **Google Analytics:** analytics.google.com, then **Reports**. Shows users, pages, traffic sources and engagement. Only visitors who accepted cookies are counted, so these figures will be lower than Cloudflare's.
- **Google Search Console:** search.google.com/search-console, then **Performance**. Shows the searches people used to find the site.
- **HostGator:** cPanel, then **Metrics**, then **Awstats**. Server-log statistics that were recorded from the day the site went live.
