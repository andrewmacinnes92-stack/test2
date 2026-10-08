"""Builds the six self-contained pages of the site.

Each page gets the shared styles, header, footer and script copied in, so every
.html file in the repository root works on its own. Edit the content here (or
base.css / components.css / site.js), then run:

    python3 _build/build.py
"""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).parent))
from services import SERVICE_PAGES, CARD, QUICK
from guides import GUIDES  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parent

PHONE = "0161 904 7800"
TEL = "tel:01619047800"
EMAIL = "nic@independentclaimsconsultants.co.uk"
SOUTH_OFFICE = "The Coach House, 3 Brooklands Close, Cobham, Surrey KT11 2DR"
HEAD_OFFICE = "Arco House, 86 Woburn Drive, Hale, Altrincham, Cheshire WA15 8NE"

# The live address of the site. Canonical links, the sitemap and social previews use it.
SITE = "https://independentclaimsconsultants.com"

# Source name (used in links throughout this file) -> folder the page is published in.
ROUTES = {
    "index.html": "",
    "claims.html": "claims/",
    "about.html": "about/",
    "advice.html": "advice/",
    "faq.html": "faq/",
    "contact.html": "contact/",
    "surrey.html": "loss-assessors-surrey/",
    "manchester.html": "loss-assessors-manchester/",
}
ROUTES.update({s["key"]: s["route"] for s in SERVICE_PAGES})

# Old addresses (the previous WordPress site and earlier versions of this one) -> new page.
REDIRECTS = {
    "contact-2/": "contact/",
    "sample-page/": "",
    "services2/": "",
    "services3/": "",
    "call-0161-768765/": "",
    "elementor-hf/independent-claims-consultants/": "",
    "elementor-hf/footer/": "",
    "claims.html": "claims/",
    "about.html": "about/",
    "advice.html": "advice/",
    "faq.html": "faq/",
    "contact.html": "contact/",
}

SITEMAP = []

ICONS = {
    "fire": '<path d="M12 2c1 3 4 5 4 9a4 4 0 0 1-8 0c0-2 1-3 1-3s-3 1-3 5a6 6 0 0 0 12 0c0-6-6-8-6-11z"/>',
    "flood": '<path d="M2 6c2-1.5 4-1.5 6 0s4 1.5 6 0 4-1.5 6 0M2 12c2-1.5 4-1.5 6 0s4 1.5 6 0 4-1.5 6 0M2 18c2-1.5 4-1.5 6 0s4 1.5 6 0 4-1.5 6 0"/>',
    "droplet": '<path d="M12 2.7 6.3 9.5a7 7 0 1 0 11.4 0z"/>',
    "storm": '<path d="M19 16.9A5 5 0 0 0 18 7h-1.3A8 8 0 1 0 4 15.3"/><path d="m13 11-4 6h6l-4 6"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "subsidence": '<path d="M3 10.5 12 3l9 7.5V21H3z"/><path d="m12 21-1.5-4 2-3-1.5-3"/>',
    "impact": '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M3 13h18"/>',
    "home": '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    "building": '<path d="M4 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16"/><path d="M16 9h2a2 2 0 0 1 2 2v10"/><path d="M2 21h20"/><path d="M8 7h4M8 11h4M8 15h4"/>',
    "key": '<circle cx="7.5" cy="15.5" r="4.5"/><path d="m10.7 12.3 9.3-9.3M17 6l3 3M14 9l2 2"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    "shieldcheck": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.5 13.2 17 22l-5-3-5 3 1.5-8.8"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "users": '<circle cx="9" cy="8" r="4"/><path d="M2 21a7 7 0 0 1 14 0"/><path d="M16 4a4 4 0 0 1 0 8M22 21a7 7 0 0 0-4-6.3"/>',
    "pound": '<path d="M17 7a5 5 0 0 0-8.5-1.5C7.6 6.6 8 9 8.5 11c.6 2.5 0 6-2.5 9h12"/><path d="M6 13h8"/>',
    "calc": '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M8 6h8M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01M8 18h8"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21l7.8-7.5 1-1.1a5.5 5.5 0 0 0 0-7.8z"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "help": '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/>',
    "tool": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
    "scale": '<path d="M12 3v18M7 21h10M5 7h14"/><path d="m5 7-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
    "box": '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
    "printer": '<path d="M6 9V2h12v7"/><rect x="2" y="9" width="20" height="9" rx="2"/><path d="M6 14h12v8H6z"/>',
    "trend": '<path d="m22 7-8.5 8.5-5-5L2 17"/><path d="M16 7h6v6"/>',
    "arrow": '<path d="M5 12h14M13 5l7 7-7 7"/>',
}


def svg(name, stroke_width="2"):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke_width}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def ic(name, cls="ic"):
    return f'<span class="{cls}" aria-hidden="true">{svg(name)}</span>'


def img(name, alt, kind="wide", cls="", eager=False):
    """Responsive WebP image from assets/img. kind: 'card' (16:10) or 'wide' (4:3)."""
    small, big = (480, 800) if kind == "card" else (640, 1100)
    h = big * 10 // 16 if kind == "card" else big * 3 // 4
    sizes = "(max-width: 960px) 100vw, 380px" if kind == "card" else "(max-width: 960px) 100vw, 540px"
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img class="{cls}" src="assets/img/{name}-{small}.webp" '
            f'srcset="assets/img/{name}-{small}.webp {small}w, assets/img/{name}-{big}.webp {big}w" '
            f'sizes="{sizes}" width="{big}" height="{h}" {load} decoding="async" alt="{html.escape(alt)}">')


def arrow_link(href, text):
    return f'<a class="link-arrow" href="{href}">{text} {svg("arrow")}</a>'


CLAIM_OPTIONS = [
    "Fire or smoke damage", "Flood", "Escape of water or leak", "Storm damage", "Theft or burglary",
    "Subsidence", "Impact damage", "Business interruption", "Something else",
]


def claim_select(id_, required=False, placeholder=False):
    opts = '\n'.join(f'              <option>{html.escape(o)}</option>' for o in CLAIM_OPTIONS)
    first = '              <option value="" disabled selected>Choose one</option>\n' if placeholder else ''
    req = ' required' if required else ''
    return f'<select id="{id_}" name="claim"{req}>\n{first}{opts}\n            </select>'


def seg(name, values, id_prefix, required=False, checked=None):
    out = []
    for v in values:
        vid = f'{id_prefix}-{re.sub(r"[^a-z]+", "-", v.lower()).strip("-")}'
        chk = ' checked' if v == checked else ''
        req = ' required' if required else ''
        out.append(f'<input type="radio" id="{vid}" name="{name}" value="{v}"{chk}{req}><label for="{vid}">{v}</label>')
    return '<div class="seg">' + ''.join(out) + '</div>'


# ---------------------------------------------------------------- shared content

CASES = [
    ("Commercial fire · Wales", "Food factory fire",
     "The claim was refused by insurers. We were instructed and obtained an excellent settlement, which enabled the business to continue trading."),
    ("Landlord fire · Glasgow", "Fire in a multi-tenancy property",
     "The tenants had been left with no help and the landlord was worried about lost rent. With our legal team and associate building company, the claim was soon sorted, the tenants moved back into a refurbished property and the landlord never lost a penny."),
    ("Commercial flood · Birmingham", "Flood at a retail store",
     "The insurers weren't happy to pay the claim. Once our legal specialists were involved, we quickly and decisively reached an excellent settlement."),
    ("Domestic fire · Manchester", "House fire",
     "Insurers had asked the homeowners to start clearing up and make a contents list. Once appointed, we moved the family to a hotel while our teams reinstated the property. They were delighted with the results."),
]

FAQS = [
    ("Loss assessors", [
        ("What is a loss assessor?",
         "<p>A loss assessor is an independent professional hired by you, the policyholder, to prepare and negotiate your insurance claim with your insurer. You are our client, so we work for you, with your interests at heart.</p>"
         "<p>Our job is to make sure you receive your full entitlement. Without professional representation, many people never receive the full value of their loss.</p>"),
        ("What's the difference between a loss assessor and a loss adjuster?",
         "<p>A loss adjuster is appointed and paid by your insurance company to investigate the claim and recommend a settlement. A loss assessor is appointed by you, works only for you, and manages and negotiates your claim to get you the best possible settlement.</p>"),
        ("My insurer is sending a loss adjuster. Why do I need you?",
         "<p>The loss adjuster visits your property and assesses the damage on behalf of your insurer. It's common practice to appoint your own representation at this point. As your loss assessor, we manage every aspect of your claim to obtain the best possible settlement for you.</p>"),
        ("What does a loss adjuster do?",
         "<p>A loss adjuster is a claims specialist appointed and paid by an insurer to investigate a complex or contentious claim. They establish the cause of the loss and whether it's covered by your policy, then report to the insurer with a recommended settlement.</p>"
         "<p>They aren't appointed to advise you on how best to make your claim, and they won't help you if you want to dispute a settlement offer. The onus is on you to prove you're entitled to more.</p>"),
        ("Will my insurance broker help with my claim?",
         "<p>If you bought your policy through a broker, they should help as far as they can. Realistically, though, few brokers have the time, resources or expertise to manage a claim, which is why many recommend using a loss assessor who can dedicate their time to it.</p>"),
    ]),
    ("Your claim", [
        ("When should I contact a loss assessor?",
         "<p>At the earliest opportunity. The start of your claim is the best time, because that's when your insurer instructs a loss adjuster to act on its behalf, not yours. If you appoint a loss assessor after the adjuster's report has gone in, it can be much harder to challenge.</p>"),
        ("How long will my claim take?",
         "<p>Every claim is different, so there are no set timescales. A straightforward, non-contentious claim generally takes between four and six weeks to settle. More complex or hard-fought claims can take longer. We don't get paid until you do, so we progress every claim as quickly and forcefully as we can.</p>"
         "<p><a href=\"a-timeline.html\">Read our guide to how long claims take</a>.</p>"),
        ("What types of claim do you manage?",
         "<p>We handle claims for homeowners, landlords and commercial clients, including fire, flood, escape of water, storm damage, impact damage, theft and subsidence.</p>"
         "<p>We also deal with alternative accommodation and, for commercial clients and landlords, loss of rent, business interruption, and stock and machinery.</p>"),
        ("How can you help me?",
         "<p>If you appoint us early, we can manage every aspect of your claim. We can:</p>"
         "<ul><li>secure your property, organise emergency works and arrange alternative accommodation where needed</li>"
         "<li>identify the full extent of the damage to buildings and contents</li>"
         "<li>prepare, present and negotiate your entire claim</li>"
         "<li>deal with your insurer and its loss adjuster so you receive the full amount you're entitled to</li>"
         "<li>help you appoint specialist surveyors and contractors, and supervise their work through to completion</li></ul>"),
    ]),
    ("Problems, costs and regulation", [
        ("My insurer has rejected my claim. Can it do that?",
         "<p>In some circumstances, yes. A policy is a contract, and an insurer can deny a claim if it believes you haven't kept to your side of it, the loss isn't covered, or it suspects fraud.</p>"
         "<p>That doesn't mean the insurer is right. We can represent you professionally and fight for the claim to be accepted and settled.</p>"
         "<p><a href=\"a-rejected.html\">Read our guide to challenging a rejected claim</a>.</p>"),
        ("What if I'm underinsured?",
         "<p>Underinsurance can have a big effect on your claim. It allows the insurer to reduce the settlement severely, and it can even reject the claim for gross underinsurance. It's more common than people think, because many people insure their property for what it's worth rather than what it would cost to rebuild.</p>"
         "<p>If you're worried about underinsurance, speak to us as soon as possible.</p>"),
        ("How much do you charge?",
         "<p>Your first consultation is free and there's no obligation. We work on a no win, no fee basis, so we don't get paid until you do. Call us and we'll talk you through how our fees work for your claim.</p>"
         "<p><a href=\"a-cost.html\">Read more about loss assessor fees</a>.</p>"),
        ("Are you regulated?",
         "<p>Yes. We're regulated by the Financial Conduct Authority (FCA Reg No 308042), and we're members of the Institute of Public Loss Assessors.</p>"),
    ]),
]


def faq_items(items):
    return '\n'.join(
        f'          <details>\n            <summary>{html.escape(q)}</summary>\n'
        f'            <div class="faq-body">{a}</div>\n          </details>'
        for q, a in items)


def faq_lookup(question):
    for _, items in FAQS:
        for q, a in items:
            if q == question:
                return (q, a)
    raise KeyError(question)


COMPARE_TABLE = """<table class="compare-table">
            <thead>
              <tr><th scope="col"><span class="visually-hidden">Question</span></th><th scope="col">Loss adjuster</th><th scope="col" class="us">Loss assessor</th></tr>
            </thead>
            <tbody>
              <tr><th scope="row">Who appoints them?</th><td>Your insurer</td><td class="us">You</td></tr>
              <tr><th scope="row">Whose interests?</th><td>The insurer's</td><td class="us">Yours, and only yours</td></tr>
              <tr><th scope="row">Prepares your claim?</th><td>No</td><td class="us">Yes, in full</td></tr>
              <tr><th scope="row">Negotiates the settlement?</th><td>For the insurer</td><td class="us">For you</td></tr>
              <tr><th scope="row">Helps you dispute an offer?</th><td>No</td><td class="us">Yes</td></tr>
              <tr><th scope="row">Who pays them?</th><td>Your insurer</td><td class="us">No win, no fee</td></tr>
            </tbody>
          </table>"""


def cta(title="Get your first consultation free",
        text="Talk to an experienced loss assessor about your claim. No win, no fee."):
    return f"""
    <section class="section">
      <div class="container">
        <div class="cta">
          <h2>{title}</h2>
          <p>{text}</p>
          <div class="cta-actions">
            <a href="contact.html" class="btn btn-light">Start your claim {svg("arrow")}</a>
            <a href="{TEL}" class="btn btn-outline-light">Call {PHONE}</a>
          </div>
          <small>Lines open Monday to Friday, 9am to 5pm.</small>
        </div>
      </div>
    </section>"""


def page_hero(pill, title, lead, extra="", image=None):
    copy = f"""
        <div class="hero-copy">
          <p class="pill"><span class="dot" aria-hidden="true"></span>{pill}</p>
          <h1>{title}</h1>
          <p class="lead">{lead}</p>
        </div>"""
    if image:
        name, alt = image
        below = f'\n        <div class="page-hero-extra">{extra}\n        </div>' if extra else ''
        return f"""
    <section class="hero page-hero">
      <div class="container page-hero-grid">
        <div>{copy}
        </div>
        <figure class="page-hero-img">{img(name, alt, eager=True)}</figure>{below}
      </div>
    </section>"""
    copy += extra
    return f"""
    <section class="hero page-hero">
      <div class="container">{copy}
      </div>
    </section>"""


def jump(links):
    return '\n        <nav class="jump" aria-label="On this page">' + ''.join(
        f'<a href="#{i}">{t}</a>' for i, t in links) + '</nav>'


# ---------------------------------------------------------------- page chrome

NAV = [("claims.html", "Claims we handle"), ("about.html", "About"), ("advice.html", "Advice"),
       ("faq.html", "FAQs"), ("contact.html", "Contact")]

LOGO = (f'<span class="logo-mark" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke-width="2.2" '
        f'stroke-linecap="round" stroke-linejoin="round">{ICONS["shield"]}</svg></span>'
        '<span class="logo-text">Independent Claims Consultants<span class="light">Loss Assessors</span></span>')


def header(active):
    home_cur = ' aria-current="page"' if active == "index.html" else ''
    items = [f'          <li class="mobile-only"><a href="index.html"{home_cur}>Home</a></li>']
    claim_keys = {s["key"] for s in SERVICE_PAGES} | {"claims.html"}
    for href, text in NAV:
        cur = ' aria-current="page"' if href == active or (href == "claims.html" and active in claim_keys) else ''
        if href == "claims.html":
            who = "".join(f'<li><a href="{k}">{CARD[k][1]}</a></li>' for k in ["home-claims.html", "commercial.html", "landlords.html"])
            kinds = "".join(f'<li><a href="{k}">{CARD[k][1].replace(" claims", "")}</a></li>'
                            for k in ["fire.html", "flood.html", "escape.html", "storm.html", "theft.html",
                                      "subsidence.html", "impact.html", "bi.html"])
            items.append(f"""          <li class="has-sub">
            <a href="{href}"{cur}>{text}</a>
            <button class="sub-toggle" type="button" aria-expanded="false" aria-controls="claims-menu"><span class="visually-hidden">Show claim types</span>{svg("arrow")}</button>
            <div class="submenu" id="claims-menu">
              <div><p class="sub-head">Who we help</p><ul>{who}</ul></div>
              <div class="types"><p class="sub-head">Claim types</p><ul>{kinds}</ul></div>
              <p class="sub-all"><a href="claims.html">All claims we handle</a></p>
            </div>
          </li>""")
            continue
        items.append(f'          <li><a href="{href}"{cur}>{text}</a></li>')
    items.append(f'          <li class="mobile-only"><a href="{TEL}">Call {PHONE}</a></li>')
    items.append('          <li><a href="contact.html" class="btn btn-primary">Start your claim</a></li>')
    nav = '\n'.join(items)
    return f"""  <a class="skip" href="#main">Skip to content</a>
  <aside class="topbar" aria-label="Contact details">
    <div class="container topbar-inner">
      <span><a href="surrey.html">Southern office: Cobham, Surrey</a><span class="sep">·</span>FCA Reg No 308042<span class="sep">·</span>Members of the IPLA</span>
      <span><a href="{TEL}">Call {PHONE}</a><span class="sep">·</span>Mon to Fri, 9am to 5pm</span>
    </div>
  </aside>

  <header class="site-header">
    <div class="container header-inner">
      <a href="index.html" class="logo" aria-label="Independent Claims Consultants home">
        {LOGO}
      </a>

      <button class="menu-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="main-nav">
        <span></span><span></span><span></span>
      </button>

      <nav class="nav" id="main-nav" aria-label="Main">
        <ul>
{nav}
        </ul>
      </nav>
    </div>
  </header>"""


FOOTER = f"""  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-about">
          <a href="index.html" class="logo" aria-label="Independent Claims Consultants home">
            {LOGO}
          </a>
          <p>Independent loss assessors helping homeowners, landlords and businesses with their insurance claims for over 30 years.</p>
          <ul class="badges">
            <li>FCA regulated</li>
            <li>IPLA members</li>
            <li>No win, no fee</li>
          </ul>
        </div>
        <div class="footer-col">
          <h3>Claims</h3>
          <ul>
            <li><a href="surrey.html">Loss assessors in Surrey</a></li>
            <li><a href="manchester.html">Loss assessors in Manchester</a></li>
            <li><a href="home-claims.html">Homeowners</a></li>
            <li><a href="commercial.html">Businesses</a></li>
            <li><a href="landlords.html">Landlords</a></li>
            <li><a href="fire.html">Fire claims</a></li>
            <li><a href="flood.html">Flood claims</a></li>
            <li><a href="bi.html">Business interruption</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3>Company</h3>
          <ul>
            <li><a href="about.html">About us</a></li>
            <li><a href="about.html#team">Our team</a></li>
            <li><a href="advice.html">Advice centre</a></li>
            <li><a href="faq.html">FAQs</a></li>
            <li><a href="contact.html">Start your claim</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3>Contact</h3>
          <ul>
            <li><a href="{TEL}">{PHONE}</a></li>
            <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
            <li><span><strong>Southern office:</strong> {SOUTH_OFFICE}</span></li>
            <li><span><strong>Head office:</strong> {HEAD_OFFICE}</span></li>
            <li><span>Monday to Friday, 9am to 5pm</span></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p class="copyright">&copy; <span id="year">2026</span> Independent Claims Consultants. Members of the Institute of Public Loss Assessors.</p>
        <p class="legal">Independent Claims Consultants is the trading name of Insurance Claims Centre UK Limited, a company registered in England No. 3932119. Regulated by the Financial Conduct Authority, FCA Reg No 308042. VAT Reg No. 519 8648 01. Registered office: Arco House, 86 Woburn Drive, Hale, Near Altrincham, Cheshire WA15 8NE.</p>
      </div>
    </div>
  </footer>
<!--CALLBAR-->
  <nav class="callbar" aria-label="Quick contact">
    <a href="{TEL}" class="btn btn-ghost">{svg("phone")} Call us</a>
    <a href="contact.html" class="btn btn-primary">Start your claim</a>
  </nav>"""

EXTRA_CSS = """
    .skip {
      position: absolute;
      top: -100px;
      left: 16px;
      z-index: 100;
      padding: 10px 16px;
      border-radius: 10px;
      background: var(--ink);
      color: #fff;
      font-weight: 600;
    }
    .skip:focus { top: 12px; }
    .visually-hidden {
      position: absolute;
      width: 1px;
      height: 1px;
      overflow: hidden;
      clip: rect(0 0 0 0);
      white-space: nowrap;
    }
    html:not(.js) [data-next], html:not(.js) [data-back], html:not(.js) .wizard-progress, html:not(.js) #sent { display: none; }
    h2[tabindex="-1"]:focus { outline: none; }"""


def link_prefix(route):
    return "../" * route.count("/")


def localise_links(doc, prefix):
    """Turn source links like about.html#team into folder links relative to this page."""
    def fix(m):
        attr, name, rest = m.group(1), m.group(2), m.group(3)
        target = prefix + ROUTES[name + ".html"]
        return f'{attr}="{target or "./"}{rest}"'
    names = "|".join(n[:-5] for n in ROUTES)
    doc = re.sub(rf'(href|action)="({names})\.html([^"]*)"', fix, doc)
    return re.sub(r'(?<=["(,\s])assets/', prefix + "assets/", doc)


def breadcrumbs(filename, label, parent=None):
    trail = [("index.html", "Home")] + ([parent] if parent else [])
    links = "".join(f'<li><a href="{f}">{n}</a></li>' for f, n in trail)
    crumbs = f"""<nav class="crumbs" aria-label="Breadcrumb"><ol>{links}<li aria-current="page">{label}</li></ol></nav>
          """
    items = trail + [(filename, label)]
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + "/" + ROUTES[f]}
            for i, (f, n) in enumerate(items)
        ],
    }
    return crumbs, data


def page(filename, title, description, main, page_css="", schema=None, callbar=True, crumb=None,
         prefix=None, indexable=True, crumb_parent=None):
    route = ROUTES.get(filename, filename)
    prefix = link_prefix(route) if prefix is None else prefix
    url = SITE + "/" + route
    css = (HERE / "base.css").read_text().rstrip("\n") + "\n\n" + (HERE / "components.css").read_text().rstrip("\n")
    js = (HERE / "site.js").read_text().rstrip("\n")
    schemas = [s for s in (schema if isinstance(schema, list) else [schema]) if s]
    if crumb:
        crumb_html, crumb_data = breadcrumbs(filename, crumb, crumb_parent)
        main = main.replace('<p class="pill">', crumb_html + '<p class="pill">', 1)
        schemas.append(crumb_data)
    schema_tag = "".join('\n  <script type="application/ld+json">\n' + json.dumps(s, indent=2, ensure_ascii=False)
                         + '\n  </script>' for s in schemas)
    if callbar:
        footer_html = FOOTER.replace("<!--CALLBAR-->\n", "")
    else:
        footer_html = FOOTER.split("<!--CALLBAR-->")[0].rstrip()
    plain_title = html.unescape(title)
    if indexable:
        seo = f"""
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Independent Claims Consultants">
  <meta property="og:locale" content="en_GB">
  <meta property="og:title" content="{html.escape(plain_title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}/assets/img/og-image.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">"""
        SITEMAP.append(url)
    else:
        seo = '\n  <meta name="robots" content="noindex">'
    doc = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{html.escape(description)}">{seo}
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
  <meta name="theme-color" content="#0f766e">
  <script>document.documentElement.classList.add('js');</script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">{schema_tag}
  <style>
{css}
{EXTRA_CSS}
{page_css}
  </style>
</head>
<body>

{header(filename)}

  <main id="main">{main}
  </main>

{footer_html}

  <script>
{js}
  </script>
</body>
</html>
"""
    out = ROOT / (route + "index.html" if route.endswith("/") or route == "" else route)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(localise_links(doc, prefix))


# ---------------------------------------------------------------- home

def home():
    who = seg("who", ["Homeowner", "Business", "Landlord"], "q", checked="Homeowner")
    quick = f"""
          <form class="quick" action="contact.html" method="get">
            <h2>See if we can help</h2>
            <p>Answer two quick questions to start your free assessment.</p>
            <fieldset class="field">
              <legend>I'm a…</legend>
              {who}
            </fieldset>
            <div class="field">
              <label for="q-claim">My claim is for…</label>
              {claim_select("q-claim")}
            </div>
            <button type="submit" class="btn btn-primary">Continue {svg("arrow")}</button>
            <p class="small">Free and with no obligation. It takes about a minute.</p>
          </form>"""

    trust = [("clock", "Over 30 years", "managing insurance claims"),
             ("award", "IPLA members", "Institute of Public Loss Assessors"),
             ("shieldcheck", "FCA regulated", "Reg No 308042"),
             ("pin", "Southern office", "Cobham, Surrey")]
    trust_html = '\n'.join(f'          <li>{ic(i)}<div><strong>{s}</strong><span class="t">{t}</span></div></li>'
                           for i, s, t in trust)

    audience_imgs = {
        "Homeowners": ("homes-bristol", "A row of colourful terraced houses on a hillside in Bristol"),
        "Businesses": ("business-warehouse", "Aisle of a warehouse with stock on tall orange racking"),
        "Landlords": ("landlord-flats", "Red-brick Victorian mansion block of flats in London"),
    }
    audiences = [
        ("home", "Homeowners", "We get you back into your home as quickly as possible, arranging emergency help and somewhere to stay while it's put right.",
         ["Buildings and contents claims", "Alternative accommodation", "Drying, repairs and reinstatement"], "home-claims.html", "Homeowner claims"),
        ("building", "Businesses", "We protect your cash flow and get you trading again, with forensic accountants calculating your business interruption loss.",
         ["Commercial fire and flood", "Business interruption", "Stock and machinery"], "commercial.html", "Business claims"),
        ("key", "Landlords", "We deal with the insurer and the repairs, and claim for the rent you lose while the property can't be let.",
         ["Loss of rent", "Multi-tenancy properties", "Reinstatement and repairs"], "landlords.html", "Landlord claims"),
    ]
    aud_html = '\n'.join(f"""          <article class="card has-img">
            {img(*audience_imgs[t], kind="card", cls="card-img")}
            <h3>{t}</h3>
            <p>{p}</p>
            <ul class="ticks">{''.join(f'<li>{x}</li>' for x in ticks)}</ul>
            {arrow_link(href, lt)}
          </article>""" for i, t, p, ticks, href, lt in audiences)

    tiles = [("fire", "Fire and smoke", "Homes, factories and multi-occupancy buildings", "fire"),
             ("flood", "Flood", "Damage from rising or flowing water", "flood"),
             ("droplet", "Escape of water", "Burst pipes, leaks and water ingress", "escape-of-water"),
             ("storm", "Storm damage", "Roofs, walls and contents", "storm"),
             ("lock", "Theft and burglary", "Stolen property and break-in damage", "theft"),
             ("subsidence", "Subsidence", "Cracking and ground movement", "subsidence"),
             ("impact", "Impact damage", "Vehicles and other impacts", "impact"),
             ("briefcase", "Business interruption", "Lost income while you recover", "business-interruption")]
    tile_pages = {"fire": "fire.html", "flood": "flood.html", "escape-of-water": "escape.html", "business-interruption": "bi.html", "storm": "storm.html", "theft": "theft.html", "subsidence": "subsidence.html", "impact": "impact.html"}
    tiles_html = '\n'.join(f'          <a class="tile" href="{tile_pages.get(a, "claims.html#" + a)}">{ic(i)}<strong>{t}</strong><span>{d}</span></a>'
                           for i, t, d, a in tiles)

    reasons = [
        ("user", "A dedicated loss assessor", "One expert runs your claim from start to finish, so you always know who to talk to."),
        ("shield", "Working only for you", "We have no ties to your insurer. Your interests are the only ones we represent."),
        ("pound", "No win, no fee", "Your first consultation is free, and we don't get paid until you do."),
        ("calc", "Specialist support", "Our legal specialists and forensic and consequential loss accountants strengthen complex claims."),
        ("award", "A century of family expertise", "The Castleton family helped establish the Institute of Public Loss Assessors."),
        ("heart", "Personal service", "Customer care and personal service have been the hallmark of our firm for three decades."),
    ]
    reasons_html = '\n'.join(f"""          <article class="card">
            {ic(i, "card-icon")}
            <h3>{t}</h3>
            <p>{p}</p>
          </article>""" for i, t, p in reasons)

    cases_html = '\n'.join(f"""          <article class="card">
            <p class="case-meta">{m}</p>
            <h3>{t}</h3>
            <p>{p}</p>
          </article>""" for m, t, p in CASES)

    areas = [("surrey-shere", "Historic timber-framed cottages in a Surrey village", "Surrey and the South East",
              "Our Southern office in Cobham covers homes and businesses across Surrey, London and the South East.",
              "surrey.html", "Loss assessors in Surrey"),
             ("manchester-street", "A busy street in Manchester city centre", "Manchester and the North West",
              "Our head office in Hale covers Greater Manchester, Cheshire and the North West.",
              "manchester.html", "Loss assessors in Manchester")]
    areas_html = '\n'.join(f"""          <article class="card has-img">
            {img(n, a, kind="card", cls="card-img")}
            <h3>{t}</h3>
            <p>{p}</p>
            {arrow_link(href, lt)}
          </article>""" for n, a, t, p, href, lt in areas)

    faq4 = [faq_lookup(q) for q in ["What is a loss assessor?", "My insurer is sending a loss adjuster. Why do I need you?",
                                     "When should I contact a loss assessor?", "How long will my claim take?"]]

    guides = [("fire", "What to do after a fire", "A step-by-step checklist for the first hours and days after a fire.", "a-fire.html"),
              ("droplet", "What to do after a flood or leak", "How to stay safe, limit the damage and protect your claim.", "a-flood.html"),
              ("help", "Answering your loss adjuster", "The questions they'll ask, why they ask them and how to answer.", "a-questions.html")]
    guides_html = '\n'.join(f"""          <article class="card">
            {ic(i, "card-icon")}
            <h3>{t}</h3>
            <p>{p}</p>
            {arrow_link(href, "Read the guide")}
          </article>""" for i, t, p, href in guides)

    steps = [("Secure your property", "We organise emergency works and arrange alternative accommodation where it's needed."),
             ("Assess the full damage", "We identify the full extent of the damage to both your buildings and contents."),
             ("Prepare and negotiate", "We prepare, present and negotiate your entire claim with your insurer and its loss adjuster."),
             ("Oversee the repairs", "We help appoint specialist surveyors and contractors, and supervise their work through to completion.")]
    steps_html = '\n'.join(f'          <li class="step"><h3>{t}</h3><p>{p}</p></li>' for t, p in steps)

    main = f"""
    <section class="hero hero-video" id="home">
      <div class="hero-media" aria-hidden="true">
        <video class="hero-bg" muted loop playsinline preload="none" poster="assets/img/hero-poster-1280.webp" data-src="assets/video/hero-firefighters"></video>
      </div>
      <div class="container hero-grid">
        <div class="hero-copy">
          <p class="pill"><span class="dot" aria-hidden="true"></span>Independent loss assessors for over 30 years</p>
          <h1>Fire or flood damage? <span>Independent loss assessors on your side.</span></h1>
          <p class="lead">When you claim, your insurer appoints a loss adjuster to protect its interests. We protect yours, managing your home or business claim from start to finish so you get everything you're entitled to.</p>
          <div class="hero-actions">
            <a href="contact.html" class="btn btn-primary">Start your claim {svg("arrow")}</a>
            <a href="{TEL}" class="btn btn-outline-light">Call {PHONE}</a>
          </div>
          <ul class="checks">
            <li>Free, no-obligation assessment</li>
            <li>No win, no fee</li>
            <li>FCA regulated</li>
          </ul>
        </div>
        <div class="hero-visual">{quick}
        </div>
      </div>
    </section>

    <section class="trust" aria-label="Why you can trust us">
      <div class="container">
        <ul>
{trust_html}
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Who we help</span>
          <h2>Expert representation for every kind of property</h2>
          <p>Whether it's your home, your business or a property you let, we take the claim off your hands.</p>
        </div>
        <div class="grid-3">
{aud_html}
        </div>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container">
        <div class="head-row">
          <div class="section-head">
            <span class="eyebrow">Claims we handle</span>
            <h2>Whatever's happened, we can help</h2>
          </div>
          {arrow_link("claims.html#types", "All claim types")}
        </div>
        <div class="grid-4">
{tiles_html}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container split wide-right">
        <div>
          <div class="section-head">
            <span class="eyebrow">Know your rights</span>
            <h2>Your insurer has an expert on its side. Shouldn't you?</h2>
          </div>
          <div class="prose">
            <p>A loss adjuster is appointed and paid by your insurance company. Their job is to investigate your claim and recommend a settlement from the insurer's point of view.</p>
            <p>A loss assessor works for you. We prepare and negotiate your claim, deal with the adjuster on your behalf and make sure nothing you're entitled to is missed.</p>
          </div>
          <p style="margin-top: 24px;">{arrow_link("a-vs.html", "Adjusters and assessors explained")}</p>
        </div>
        <div>
          {COMPARE_TABLE}
        </div>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">How it works</span>
          <h2>We manage every aspect of your claim</h2>
          <p>From the first call to the final settlement, your dedicated loss assessor takes care of it all.</p>
        </div>
        <ol class="steps">
{steps_html}
        </ol>
        <p class="note">{svg("info")}<span><strong>The earlier, the better.</strong> Contact us at the start of your claim. Once your insurer's loss adjuster has reported, it can be much harder to challenge their findings.</span></p>
      </div>
    </section>

    <section class="stats" aria-label="Independent Claims Consultants in numbers">
      <div class="container">
        <span class="eyebrow">By the numbers</span>
        <h2>Decades of experience, working only for you</h2>
        <ul>
          <li><span class="stat-num"><span data-count="30">30</span><span class="unit">+</span></span><span class="t">years managing insurance claims</span></li>
          <li><span class="stat-num"><span data-count="100">100</span><span class="unit">+</span></span><span class="t">years of family history in loss assessment</span></li>
          <li><span class="stat-num"><span data-count="2">2</span></span><span class="t">UK offices: Cobham, Surrey and Hale, Cheshire</span></li>
          <li><span class="stat-num"><span class="unit">£</span>0</span><span class="t">to get started: free first consultation, no win, no fee</span></li>
        </ul>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Why choose us</span>
          <h2>Experience you can rely on</h2>
        </div>
        <div class="grid-3">
{reasons_html}
        </div>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container">
        <div class="head-row">
          <div class="section-head">
            <span class="eyebrow">Recent cases</span>
            <h2>Real results for our clients</h2>
          </div>
          {arrow_link("about.html", "More about us")}
        </div>
        <div class="grid-2">
{cases_html}
        </div>
      </div>
    </section>

    <section class="section" id="areas">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Areas we cover</span>
          <h2>Local loss assessors, nationwide reach</h2>
          <p>We visit you at your property, wherever you are in the UK, from our two offices.</p>
        </div>
        <div class="grid-2">
{areas_html}
        </div>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">FAQs</span>
            <h2>Common questions</h2>
            <p>Quick answers to the questions people ask us most.</p>
          </div>
          {arrow_link("faq.html", "See all FAQs")}
        </div>
        <div class="faq">
{faq_items(faq4)}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="head-row">
          <div class="section-head">
            <span class="eyebrow">Advice centre</span>
            <h2>Helpful guides for your claim</h2>
          </div>
          {arrow_link("advice.html", "Visit the advice centre")}
        </div>
        <div class="grid-3">
{guides_html}
        </div>
      </div>
    </section>
{cta()}"""

    css = """
    /* ---------- Homepage ---------- */
    .hero-grid {
      display: grid;
      grid-template-columns: 1.05fr 0.95fr;
      gap: 56px;
      align-items: center;
    }
    .hero { padding-bottom: 88px; }
    .hero h1 { font-size: clamp(2.3rem, 4.4vw, 3.3rem); }
    @media (max-width: 960px) {
      .hero-grid { grid-template-columns: 1fr; gap: 44px; }
      .hero-visual { max-width: 520px; }
    }"""

    schema = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": "Independent Claims Consultants",
        "url": SITE + "/",
        "logo": SITE + "/assets/apple-touch-icon.png",
        "image": SITE + "/assets/img/og-image.jpg",
        "legalName": "Insurance Claims Centre UK Limited",
        "description": "Independent loss assessors helping homeowners, landlords and businesses with fire, flood and other insurance claims.",
        "telephone": "+44 161 904 7800",
        "email": EMAIL,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "The Coach House, 3 Brooklands Close",
            "addressLocality": "Cobham",
            "addressRegion": "Surrey",
            "postalCode": "KT11 2DR",
            "addressCountry": "GB",
        },
        "parentOrganization": {
            "@type": "Organization",
            "name": "Independent Claims Consultants (head office)",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Arco House, 86 Woburn Drive",
                "addressLocality": "Hale, Altrincham",
                "addressRegion": "Cheshire",
                "postalCode": "WA15 8NE",
                "addressCountry": "GB",
            },
        },
        "openingHours": "Mo-Fr 09:00-17:00",
        "areaServed": "GB",
    }
    page("index.html", "Loss Assessors Surrey &amp; the South | Independent Claims Consultants",
         "Independent loss assessors in Cobham, Surrey. Over 30 years helping homeowners, landlords and businesses with fire and flood insurance claims. No win, no fee.",
         main, css, schema)


# ---------------------------------------------------------------- claims

def mini_grid(items):
    return '\n'.join(f'            <div class="mini">{ic(i)}<div><strong>{t}</strong><p>{p}</p></div></div>'
                     for i, t, p in items)


def claims():
    homeowner = [
        ("shield", "Emergency help", "We secure your property and organise urgent works."),
        ("home", "Alternative accommodation", "Somewhere to stay while your home is put right."),
        ("file", "Buildings and contents", "We identify the full extent of the damage to both."),
        ("droplet", "Drying and sanitising", "Thorough drying so damp and dry rot don't follow."),
        ("tool", "Repairs overseen", "We appoint and supervise surveyors and contractors."),
        ("scale", "Full negotiation", "We negotiate your settlement with the insurer and its adjuster."),
    ]
    business = [
        ("fire", "Commercial fire and flood", "Complete claims management for damaged premises."),
        ("trend", "Business interruption", "Forensic and consequential loss accountants calculate your lost income."),
        ("box", "Stock and machinery", "We make sure damaged stock and equipment are fully valued."),
        ("check", "Ready for liability", "Everything in place for the moment your insurer accepts liability."),
        ("briefcase", "Back to trading", "We work to get you operational again as quickly as possible."),
        ("scale", "Legal specialists", "Expert support when an insurer resists your claim."),
    ]
    landlord = [
        ("pound", "Loss of rent", "We claim for the rent you lose while the property can't be let."),
        ("users", "Multi-tenancy properties", "Experience with complex buildings and several tenants."),
        ("tool", "Reinstatement", "Our associate building company can carry out the repairs."),
        ("scale", "Full negotiation", "We deal with the insurer so you don't have to."),
    ]

    block_imgs = {
        "homeowners": ("homes-terrace", "Victorian terraced houses on a street in Oxford"),
        "businesses": ("business-stock", "Warehouse interior with goods on shelving"),
        "landlords": ("landlord-flats", "Red-brick Victorian mansion block of flats in London"),
    }

    hub_pages = {"homeowners": "home-claims.html", "businesses": "commercial.html", "landlords": "landlords.html"}
    hub_labels = {"homeowners": "Home insurance claims", "businesses": "Commercial claims", "landlords": "Landlord claims"}

    def block(id_, eyebrow, title, text, items, who, soft=False):
        return f"""
    <section class="section{' section-soft' if soft else ''}" id="{id_}">
      <div class="container audience-block">
        <div>
          <div class="section-head">
            <span class="eyebrow">{eyebrow}</span>
            <h2>{title}</h2>
            <p>{text}</p>
          </div>
          <p class="block-links">{arrow_link(hub_pages[id_], hub_labels[id_])}{arrow_link("contact.html?who=" + who, "Start a " + who.lower() + " claim")}</p>
          {img(*block_imgs[id_], kind="card", cls="block-img")}
        </div>
        <div class="mini-grid">
{mini_grid(items)}
        </div>
      </div>
    </section>"""

    types = [
        ("fire", "fire", "Fire and smoke",
         "After a fire you'll face a number of critical decisions, and each one affects the outcome of your claim. We guide you through the whole fire claims process, from securing the building to restoring it, so you understand your options at every stage."),
        ("flood", "flood", "Flood",
         "A flood means a complicated claim, contractors to engage and oversee, and an insurer to negotiate with. We manage all of it, and make sure your property is thoroughly dried and sanitised by an experienced restoration company."),
        ("escape-of-water", "droplet", "Escape of water",
         "Burst pipes, leaks and water ingress can cause damage that isn't always visible straight away. We make sure the full extent of the damage is found and included in your claim."),
        ("storm", "storm", "Storm damage",
         "Storm damage to roofs, walls and contents needs fast action to stop further harm. We arrange emergency works and present a complete claim for the damage."),
        ("theft", "lock", "Theft and burglary",
         "A break-in often means damage to doors, windows and locks as well as stolen belongings. We help you build a complete list of what was taken and claim for everything you've lost."),
        ("subsidence", "subsidence", "Subsidence",
         "Subsidence claims are often long and technical. We work with specialist surveyors to establish the cause and extent of the movement, then negotiate the repairs and settlement."),
        ("impact", "impact", "Impact damage",
         "Whether a vehicle has hit your property or something has fallen onto it, we deal with the insurer and make sure the repairs are fully covered."),
        ("business-interruption", "trend", "Business interruption",
         "Business interruption claims are rarely simple, and the way insurers present them can make them more complex. Our forensic and consequential loss accountants accurately calculate your loss, protecting your business while the building is restored."),
    ]
    type_pages = {"fire": "fire.html", "flood": "flood.html", "escape-of-water": "escape.html", "business-interruption": "bi.html", "storm": "storm.html", "theft": "theft.html", "subsidence": "subsidence.html", "impact": "impact.html"}
    types_html = '\n'.join(f"""          <article class="card type-card" id="{a}">
            {ic(i)}
            <h3>{t}</h3>
            <p>{p}</p>{chr(10) + "            " + arrow_link(type_pages[a], "Find out more") if a in type_pages else ""}
          </article>""" for a, i, t, p in types)

    main = page_hero(
        "Claims we handle", "Insurance claims <span>we handle</span>",
        "We represent homeowners, landlords and businesses across the UK, managing every kind of property insurance claim from start to finish.",
        image=("inspector", "Assessor in a hard hat and hi-vis vest inspecting a window in an empty room"),
        extra=jump([("homeowners", "Homeowners"), ("businesses", "Businesses"), ("landlords", "Landlords"),
              ("types", "Claim types"), ("disputed", "Refused claims")]))
    main += block("homeowners", "Homeowners", "Getting you back home",
                  "The aftermath of a fire, flood or break-in can have a huge emotional impact on you and your family, and dealing with an insurance claim on top is a lot to ask. Your dedicated loss assessor takes it on for you.",
                  homeowner, "Homeowner")
    main += block("businesses", "Businesses", "Keeping your business trading",
                  "Damage to your premises can put your whole business at risk. Insurers won't pay until they're satisfied they're liable and that you've met your policy conditions, and delays can hit cash flow hard. We take control of the claim so you can focus on your customers.",
                  business, "Business", soft=True)
    main += block("landlords", "Landlords", "Protecting your rental income",
                  "When a let property is damaged, you're dealing with tenants, lost rent and your insurer all at once. We handle the claim and the reinstatement so the property can be lived in again.",
                  landlord, "Landlord")
    main += f"""
    <section class="section section-soft" id="types">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Claim types</span>
          <h2>Types of claim we manage</h2>
          <p>We handle every kind of property damage claim. Here are the most common.</p>
        </div>
        <div class="grid-2">
{types_html}
        </div>
      </div>
    </section>

    <section class="section" id="disputed">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">Problems with your claim?</span>
            <h2>Claim refused or underinsured? We can still help</h2>
          </div>
          <div class="prose">
            <p>An insurer can refuse a claim if it believes you haven't kept to the policy conditions, the loss isn't covered, or it suspects fraud. That doesn't mean it's right. We represent you professionally and fight for the claim to be accepted and settled.</p>
            <p>Underinsurance lets an insurer reduce a settlement severely, and it's more common than people think. Many people insure their property for what it's worth rather than what it would cost to rebuild. If you're worried, speak to us as soon as possible.</p>
          </div>
        </div>
        <div class="grid-2" style="grid-template-columns: 1fr;">
          <article class="card">
            <p class="case-meta">{CASES[0][0]}</p>
            <h3>Refused, then settled</h3>
            <p>{CASES[0][2]}</p>
          </article>
          <article class="card">
            <p class="case-meta">{CASES[2][0]}</p>
            <h3>Insurer reluctant to pay</h3>
            <p>{CASES[2][2]}</p>
          </article>
        </div>
      </div>
    </section>
{cta()}"""
    page("claims.html", "Fire, Flood &amp; Property Claims | Independent Claims Consultants",
         "Loss assessors for homeowners, businesses and landlords: fire, flood, escape of water, storm, theft, subsidence, impact damage and business interruption claims.",
         main, crumb="Claims we handle")


# ---------------------------------------------------------------- about

def about():
    creds = """
        <ul class="creds">
          <li><strong>IPLA members</strong><span>Institute of Public Loss Assessors</span></li>
          <li><strong>FCA regulated</strong><span>Reg No 308042</span></li>
          <li><strong>UK offices</strong><span>Cobham (Surrey) and Hale (Manchester)</span></li>
        </ul>"""
    team = [
        ("NC", "Nic Castleton", "Managing Director", "Head office, Hale",
         "\"Your specialist loss assessor will ensure your claim is processed as quickly as possible, with everything in place ready for the moment liability is accepted.\""),
        ("AM", "Andrew MacInnes", "Loss Assessor", "Southern office, Cobham",
         "\"Every client is assigned a dedicated loss assessor. Their experience will ensure your claim is run smoothly and efficiently.\""),
        ("NM", "Neil Munnerley", "Loss Assessor", "Southern office, Cobham",
         "One of our dedicated loss assessors, managing claims for homeowners, landlords and businesses from first visit to final settlement."),
        ("NH", "Nigel Hennerley", "Loss Assessor", "Head office, Hale",
         "\"You will have peace of mind knowing your loss assessor will guide you through the entire claims process.\""),
        ("RY", "Ralph Yarwood-Smith", "Technician", None,
         "One of our technicians, supporting our loss assessors on claims."),
        ("MP", "Mark Pepper", "Technician", None,
         "One of our technicians, supporting our loss assessors on claims."),
    ]
    team_html = '\n'.join(f"""          <article class="card member">
            <span class="avatar" aria-hidden="true">{i}</span>
            <h3>{n}</h3>
            <p class="role">{r}</p>
            {f'<p class="office">{svg("pin")}{o}</p>' if o else ''}
            <p>{q}</p>
          </article>""" for i, n, r, o, q in team)
    offices = [("Southern office", SOUTH_OFFICE),
               ("Head office", HEAD_OFFICE)]
    offices_html = '\n'.join(f"""          <article class="card">
            {ic("pin")}
            <h3 style="margin-top: 18px;">{t}</h3>
            <p>{a}</p>{chr(10) + "            " + arrow_link("surrey.html" if t == "Southern office" else "manchester.html", "Loss assessors in Surrey" if t == "Southern office" else "Loss assessors in Manchester")}
          </article>""" for t, a in offices)

    main = page_hero(
        "About us", "On your side for <span>over 30 years.</span>",
        "Independent Claims Consultants helps homeowners, landlords and businesses across the UK recover from fire, flood and other disasters, and get everything they're entitled to.",
        creds, image=("adviser-woman", "A female adviser going through paperwork with clients at a table"))
    main += f"""

    <section class="section">
      <div class="container split">
        <div>
          <div class="section-head">
            <span class="eyebrow">Our story</span>
            <h2>A family tradition in loss assessment</h2>
          </div>
          <div class="prose">
            <p>It's over 100 years since the Castleton family first entered the complex and specialised world of loss assessment. It was at the family's instigation that the Institute of Public Loss Assessors was established, and Nic Castleton's grandfather was chosen as its president.</p>
            <p>Nic founded Independent Claims Consultants three decades ago. Since then, the firm has helped individuals and businesses recover from a wide range of disasters, with every client assigned a dedicated loss assessor.</p>
            <p>When you make a claim, your insurer appoints a loss adjuster to work in its interests. We work only in yours, using our expertise to get you the best possible settlement.</p>
          </div>
        </div>

        <figure class="quote">
          <blockquote>Since establishing Independent Claims Consultants three decades ago, I have never lost sight of the long running tradition of customer care and personal service which is the hallmark of my family's long history in loss assessment.</blockquote>
          <figcaption>
            <span class="avatar" aria-hidden="true">NC</span>
            <div><strong>Nic Castleton</strong><span>Managing Director</span></div>
          </figcaption>
        </figure>
      </div>
    </section>

    <section class="section section-soft" id="team">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Our team</span>
          <h2>Your dedicated loss assessors</h2>
          <p>Every client has their own loss assessor, backed by our technicians, legal specialists and forensic and consequential loss accountants.</p>
        </div>
        <div class="grid-3 team-grid">
{team_html}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Accreditations</span>
          <h2>Regulated and accountable</h2>
        </div>
        <div class="grid-2">
          <article class="card">
            {ic("award", "card-icon")}
            <h3>Institute of Public Loss Assessors</h3>
            <p>We're members of the Institute of Public Loss Assessors, the professional body our founder's family helped establish.</p>
          </article>
          <article class="card">
            {ic("shieldcheck", "card-icon")}
            <h3>Financial Conduct Authority</h3>
            <p>Claims management is a regulated activity in the UK. We're regulated by the Financial Conduct Authority under FCA Reg No 308042.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-soft" id="offices">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Our offices</span>
          <h2>Covering the whole of the UK</h2>
          <p>We help clients across the country from our offices in Surrey and the North West.</p>
        </div>
        <div class="grid-2">
{offices_html}
        </div>
      </div>
    </section>
{cta()}"""
    page("about.html", "About Our Loss Assessors | Independent Claims Consultants",
         "Independent Claims Consultants: family-run UK loss assessors with over 30 years' experience, members of the Institute of Public Loss Assessors and regulated by the FCA.",
         main, crumb="About us")


# ---------------------------------------------------------------- advice

def checklist(items):
    return '\n'.join(f'            <li><div><strong>{t}</strong><span>{d}</span></div></li>' for t, d in items)


ARTICLES = {
    "a-fire.html": ("advice/what-to-do-after-a-fire/", "fire", "What to do after a fire",
                    "A step-by-step checklist for the first hours and days after a fire, and the mistakes to avoid."),
    "a-flood.html": ("advice/what-to-do-after-a-flood/", "droplet", "What to do after a flood or leak",
                     "How to stay safe, limit the damage and protect your claim after flood or escape of water."),
    "a-questions.html": ("advice/loss-adjuster-questions/", "help", "Questions your loss adjuster may ask",
                         "What a loss adjuster will ask you, why they ask it and how to answer."),
    "a-vs.html": ("advice/loss-adjuster-vs-loss-assessor/", "scale", "Loss adjuster vs loss assessor",
                  "Who they work for, what they do and why it pays to have your own representation."),
    "a-under.html": ("advice/underinsurance/", "pound", "Underinsurance explained",
                     "How being underinsured can reduce your settlement, and how to check your cover."),
    "a-rejected.html": ("advice/insurance-claim-rejected/", "scale", "My insurance claim was rejected: what now?",
                        "Why claims are turned down or reduced, how to challenge the decision and where to complain."),
    "a-cost.html": ("advice/how-much-does-a-loss-assessor-cost/", "pound", "How much does a loss assessor cost?",
                    "How loss assessor fees work, what no win, no fee means and when it's worth appointing one."),
    "a-accommodation.html": ("advice/alternative-accommodation/", "home", "Alternative accommodation after a fire or flood",
                             "What your policy may pay for if you can't live at home, and how to make sure it's arranged properly."),
    "a-timeline.html": ("advice/how-long-does-an-insurance-claim-take/", "clock", "How long does an insurance claim take?",
                        "The stages of a property claim, what slows it down and how to keep yours moving."),
    "a-glossary.html": ("advice/insurance-claim-glossary/", "file", "Insurance claim glossary",
                        "Plain-English definitions of the terms you'll hear during a claim."),
}
ROUTES.update({k: v[0] for k, v in ARTICLES.items()})

PUBLISHED = "2026-10-08"


def article_page(key, title, description, h1, lead, body, related, image=None, extra_schema=None):
    route, icon, name, _ = ARTICLES[key]
    main = page_hero("Advice centre", h1, lead, image=image)
    main += body
    rel = "\n".join(
        f'          <a class="tile" href="{k}">{ic(ARTICLES[k][1])}<strong>{ARTICLES[k][2]}</strong><span>{ARTICLES[k][3]}</span></a>'
        for k in related)
    main += f"""

    <section class="section section-soft">
      <div class="container">
        <div class="head-row">
          <div class="section-head">
            <span class="eyebrow">Keep reading</span>
            <h2>More from our advice centre</h2>
          </div>
          {arrow_link("advice.html", "All guides")}
        </div>
        <div class="grid-3">
{rel}
        </div>
      </div>
    </section>
{cta("Need help with your claim?", "Speak to an experienced loss assessor for free, no-obligation advice. No win, no fee.")}"""
    schema = [{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": name,
        "description": description,
        "url": SITE + "/" + route,
        "image": SITE + "/assets/img/" + (image[0] + "-1100.webp" if image else "og-image.jpg"),
        "datePublished": PUBLISHED,
        "dateModified": __import__("datetime").date.today().isoformat(),
        "author": {"@type": "Organization", "name": "Independent Claims Consultants", "url": SITE + "/"},
        "publisher": {"@type": "Organization", "name": "Independent Claims Consultants",
                      "logo": {"@type": "ImageObject", "url": SITE + "/assets/apple-touch-icon.png"}},
    }] + (extra_schema or [])
    page(key, title, description, main, schema=schema, crumb=name, crumb_parent=("advice.html", "Advice centre"))


def mistakes(items):
    return "\n".join(f"            <li><div><strong>{t}</strong><span>{d}</span></div></li>" for t, d in items)


def advice():
    # ------------------------------------------------------------------ hub
    cards = "\n".join(f"""          <article class="card">
            {ic(icon, "card-icon")}
            <h3>{name}</h3>
            <p>{blurb}</p>
            {arrow_link(k, "Read the guide")}
          </article>""" for k, (route, icon, name, blurb) in ARTICLES.items())
    claim_links = "\n".join(
        f'          <a class="tile" href="{k}">{ic(CARD[k][0])}<strong>{CARD[k][1]}</strong><span>{CARD[k][2]}</span></a>'
        for k in ["fire.html", "flood.html", "escape.html", "storm.html"])
    main = page_hero(
        "Advice centre", "Practical help <span>for your claim</span>",
        "Clear guidance on what to do after a fire or flood, how to deal with your insurer's loss adjuster, and the terms you'll come across along the way.",
        image=("policy-woman", "A smiling female adviser holding a policy document"))
    main += f"""

    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Guides</span>
          <h2>Insurance claim guides</h2>
          <p>Written by our loss assessors to help you protect your claim from day one.</p>
        </div>
        <div class="grid-3">
{cards}
        </div>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container">
        <div class="head-row">
          <div class="section-head">
            <span class="eyebrow">By claim type</span>
            <h2>Help with a specific claim</h2>
          </div>
          {arrow_link("claims.html", "All claims we handle")}
        </div>
        <div class="grid-4">
{claim_links}
        </div>
      </div>
    </section>
{cta("Need help with your claim?", "Speak to an experienced loss assessor for free, no-obligation advice. No win, no fee.")}"""
    page("advice.html", "Insurance Claim Advice | Independent Claims Consultants",
         "Practical guides from our loss assessors: what to do after a fire or flood, answering your loss adjuster, underinsurance and a glossary of claim terms.",
         main, crumb="Advice centre")

    def check_body(intro_head, intro, items, img_spec, extra_head, extra_intro, extra_items, claim_links):
        intro_html = "\n".join(f"            <p>{p}</p>" for p in intro)
        links = "".join(arrow_link(k, t) for k, t in claim_links)
        return f"""

    <section class="section">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">Checklist</span>
            <h2>{intro_head}</h2>
          </div>
          <div class="prose">
{intro_html}
          </div>
          <button type="button" class="btn btn-ghost print-btn no-print" data-print>{svg("printer")} Print this checklist</button>
          {img(*img_spec, cls="block-img no-print")}
        </div>
        <ol class="checklist">
{checklist(items)}
        </ol>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">Avoid these</span>
            <h2>{extra_head}</h2>
            <p>{extra_intro}</p>
          </div>
          <p class="block-links">{links}</p>
        </div>
        <ul class="checklist ticklist">
{mistakes(extra_items)}
        </ul>
      </div>
    </section>"""

    # ------------------------------------------------------------------ after a fire
    fire = [
        ("Make sure everyone is safe", "Don't go back inside until the fire service tells you it's safe."),
        ("Tell your insurer", "Report the fire as soon as you can and note your claim reference."),
        ("Secure the property", "Board up doors and windows to prevent further damage or theft. Keep receipts for any emergency costs."),
        ("Photograph everything", "Take photos and videos of all the damage before anything is moved or cleaned."),
        ("Keep damaged items", "Don't throw anything away until your insurer has agreed. Damaged items are evidence."),
        ("Don't rush into an offer", "Don't accept a settlement or sign anything until you understand your full entitlement."),
        ("Speak to a loss assessor early", "Ideally before the loss adjuster visits, so you're represented from the start."),
    ]
    fire_mistakes = [
        ("Throwing damaged items away", "Without the items, or at least clear photos, it's much harder to prove what was lost."),
        ("Underestimating smoke damage", "Smoke and soot spread well beyond the fire itself and can affect rooms that look untouched."),
        ("Starting permanent repairs too soon", "Emergency work is fine, but get permanent repairs agreed before they start."),
        ("Accepting the first offer", "An early offer may not reflect everything your policy covers."),
        ("Waiting to get advice", "Once the loss adjuster has reported, it can be much harder to challenge their findings."),
    ]
    article_page(
        "a-fire.html", "What to Do After a House Fire: Checklist | Independent Claims Consultants",
        "What to do after a house or business fire: a step-by-step checklist to keep you safe and protect your insurance claim, plus the mistakes to avoid.",
        "What to do <span>after a fire</span>",
        "The first few days after a fire are overwhelming. These steps protect you, your property and your insurance claim.",
        check_body(
            "The first steps after a fire",
            ["After a fire, safety comes first. Once everyone is safe, the decisions you make in the first few days can have a direct impact on the outcome of your insurance claim.",
             "Work through this checklist, keep a note of everything you do and spend, and get advice before agreeing anything with your insurer."],
            fire, ("fire-hose", "Firefighters directing a hose at a fire"),
            "Common mistakes after a fire",
            "These are the mistakes we see most often, and each one can reduce what you receive.",
            fire_mistakes, [("fire.html", "Fire damage claims")]),
        ["a-questions.html", "a-vs.html", "a-under.html"])

    # ------------------------------------------------------------------ after a flood
    flood = [
        ("Stay safe", "Avoid floodwater, which can be contaminated. Only turn off the electricity at the mains if it's safe to do so."),
        ("Stop the water if you can", "For a burst pipe or leak, turn off the water at the stopcock."),
        ("Tell your insurer", "Report the damage promptly and note your claim reference."),
        ("Record the damage", "Photograph and video every affected room, and note how high the water reached."),
        ("Keep damaged items", "Don't throw anything away until your insurer has seen it or agreed."),
        ("Don't start repairs too soon", "Get emergency drying and urgent works agreed first, and keep every receipt."),
        ("Get your own representation", "A loss assessor makes sure your property is properly dried and your claim covers all the damage."),
    ]
    flood_mistakes = [
        ("Repairing before the building is dry", "Repairs should wait until moisture readings confirm the property is dry, or damp and mould can follow."),
        ("Cleaning up before photographing", "Record the damage first. Photos and videos are some of your best evidence."),
        ("Claiming under the wrong section", "Flood from outside and escape of water from inside are treated differently by most policies."),
        ("Not keeping receipts", "Emergency costs such as pumps, dehumidifiers and temporary repairs can usually be claimed."),
        ("Not checking alternative accommodation cover", "If your home can't be lived in, your policy may pay for somewhere to stay."),
    ]
    article_page(
        "a-flood.html", "What to Do After a Flood or Leak | Independent Claims Consultants",
        "What to do after a flood, burst pipe or leak: a step-by-step checklist to stay safe, limit the damage and protect your insurance claim.",
        "What to do <span>after a flood or leak</span>",
        "Water damage spreads quickly. Acting fast limits the damage and protects your insurance claim.",
        check_body(
            "The first steps after water damage",
            ["Whether the water came from a river, heavy rain or a burst pipe, the first priority is safety. Floodwater can be contaminated, and water and electricity are a dangerous mix.",
             "Then concentrate on stopping further damage and recording what's happened. Proper drying matters as much as the repairs themselves."],
            flood, ("water-damage", "Standing water across the floor of an empty room"),
            "Common mistakes after a flood or leak",
            "Avoid these and you'll protect both your property and your claim.",
            flood_mistakes, [("flood.html", "Flood damage claims"), ("escape.html", "Escape of water claims")]),
        ["a-fire.html", "a-under.html", "a-questions.html"])

    # ------------------------------------------------------------------ loss adjuster questions
    questions = [
        ("What happened?", "To compare your account with what your policy covers.",
         "Stick to the facts you know. Don't guess or exaggerate.",
         "We help you give a clear, accurate account from the start."),
        ("When did it happen?", "To check the loss falls within your policy period and was reported promptly.",
         "Be as precise as you can about the date and time.",
         "We make sure your timeline matches the other evidence, such as photos and reports."),
        ("Can you prove what you owned?", "To validate the items you're claiming for.",
         "Gather receipts, invoices, bank statements, photos and manuals where you can.",
         "We build a thorough list of everything you've lost to present to the adjuster."),
        ("How much is your property insured for?", "To check whether you're underinsured, which can reduce your settlement.",
         "Have your policy schedule to hand and answer accurately.",
         "If underinsurance is raised, we challenge it and fight for every penny you're entitled to."),
        ("Have you started any repairs?", "To check any work was necessary and the costs are reasonable.",
         "Explain any emergency work you've had done and provide photos and receipts.",
         "We make sure reasonable emergency costs are included in your claim."),
        ("Have you made any previous claims?", "To check your claims history and what you told the insurer when you took out the policy.",
         "Answer honestly and accurately.",
         "We help make sure your answers are complete and correct."),
    ]
    q_html = '\n'.join(f"""          <article class="card">
            <h3>"{q}"</h3>
            <div class="qa-part"><b>Why they ask</b><p>{w}</p></div>
            <div class="qa-part"><b>How to answer</b><p>{a}</p></div>
            <div class="qa-part"><b>How we help</b><p>{h}</p></div>
          </article>""" for q, w, a, h in questions)
    prepare = [
        ("Your policy schedule and wording", "So you know what you're covered for, and for how much."),
        ("Photos and videos of the damage", "Taken before anything was moved, cleaned or repaired."),
        ("A list of damaged and lost items", "With approximate ages and values where you know them."),
        ("Receipts for emergency costs", "Such as boarding up, drying equipment and temporary accommodation."),
        ("A note of what happened", "Dates, times and a simple timeline while it's fresh in your mind."),
        ("Your loss assessor", "If you've appointed one, they can attend the visit with you."),
    ]
    article_page(
        "a-questions.html", "Questions Your Loss Adjuster May Ask | Independent Claims Consultants",
        "The questions a loss adjuster is likely to ask after a fire, flood or other insurance claim, why they ask them and how to answer, plus how to prepare for the visit.",
        "Questions your loss adjuster <span>may ask</span>",
        "A loss adjuster's questions help your insurer decide whether to pay, and how much. Here's what to expect and how to prepare.",
        f"""

    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">The visit</span>
          <h2>What they'll ask, and why</h2>
          <p>Answer clearly and honestly, stick to the facts, and don't guess. If you're not sure, say so and come back to them.</p>
        </div>
        <div class="grid-2">
{q_html}
        </div>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">Be prepared</span>
            <h2>Before the loss adjuster visits</h2>
            <p>Having these ready makes the visit smoother and your claim stronger.</p>
          </div>
          {arrow_link("a-vs.html", "Why your own representation matters")}
        </div>
        <ul class="checklist ticklist">
{mistakes(prepare)}
        </ul>
      </div>
    </section>""",
        ["a-vs.html", "a-under.html", "a-fire.html"],
        image=("inspector", "An inspector in a hard hat checking a window"))

    # ------------------------------------------------------------------ adjuster vs assessor
    vs_faqs = [faq_lookup(q) for q in ["What is a loss assessor?", "What does a loss adjuster do?",
                                        "My insurer is sending a loss adjuster. Why do I need you?",
                                        "When should I contact a loss assessor?"]]
    article_page(
        "a-vs.html", "Loss Adjuster vs Loss Assessor: The Difference | Independent Claims Consultants",
        "What's the difference between a loss adjuster and a loss assessor? Who they work for, what they do, who pays them and why it pays to appoint your own.",
        "Loss adjuster <span>vs loss assessor</span>",
        "They sound alike, but they work for different people. Here's the difference, and why it matters for your claim.",
        f"""

    <section class="section">
      <div class="container split top wide-right">
        <div>
          <div class="section-head">
            <span class="eyebrow">Know the difference</span>
            <h2>Two experts, two sides</h2>
          </div>
          <div class="prose">
            <p>A loss adjuster is appointed and paid by your insurer to investigate a complex or contentious claim. They establish the cause of the loss, check whether it's covered by your policy and report back with a recommended settlement. They review your claim from the insurer's point of view.</p>
            <p>They aren't appointed to advise you on making your claim, and they won't help if you want to dispute their recommendation. The onus is on you to prove you're entitled to more.</p>
            <p>A loss assessor is appointed by you. We prepare and negotiate your claim and fight your corner. It pays to appoint one early: once the adjuster's report has been submitted, it can be very difficult to challenge.</p>
          </div>
        </div>
        <div>
          {COMPARE_TABLE}
        </div>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">FAQs</span>
            <h2>Common questions</h2>
          </div>
          {arrow_link("faq.html", "See all FAQs")}
        </div>
        <div class="faq">
{faq_items(vs_faqs)}
        </div>
      </div>
    </section>""",
        ["a-questions.html", "a-under.html", "a-glossary.html"],
        image=("adviser-woman", "A female adviser going through paperwork with clients at a table"),
        extra_schema=[{
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer",
                            "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a)).strip()}} for q, a in vs_faqs]}])

    # ------------------------------------------------------------------ underinsurance
    check_cover = [
        ("Insure for the rebuild cost", "Your buildings sum insured should reflect what it would cost to rebuild, not the market value."),
        ("Include everything", "Outbuildings, garages, walls and extensions all add to the rebuild cost."),
        ("Value your contents properly", "Go room by room. Most people underestimate the cost of replacing everything."),
        ("List high-value items", "Jewellery, art and other valuables above the single-item limit usually need to be named."),
        ("Review every year", "Building costs and your belongings change. Check your sums insured at each renewal."),
        ("Get professional advice", "For larger or older properties, a surveyor's rebuild valuation is worth considering."),
    ]
    article_page(
        "a-under.html", "Underinsurance Explained | Independent Claims Consultants",
        "What underinsurance is, how it can reduce your insurance settlement, a worked example, and how to check you're properly covered.",
        "Underinsurance <span>explained</span>",
        "Being underinsured can reduce your settlement, sometimes severely. Here's how it works and how to protect yourself.",
        f"""

    <section class="section">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">What it means</span>
            <h2>What is underinsurance?</h2>
          </div>
          <div class="prose">
            <p>You're underinsured when your sum insured is less than it would really cost to rebuild your property or replace its contents. Your insurer can then reduce your settlement, sometimes severely, and in cases of gross underinsurance it can reject the claim altogether.</p>
            <p>It's often unintentional. Many people insure their property for what it's worth on the market rather than what it would cost to rebuild.</p>
            <p>It isn't always as clear-cut as an insurer may suggest. If you're worried about underinsurance, talk to us as early as possible.</p>
          </div>
        </div>
        <aside class="card">
          {ic("calc", "card-icon")}
          <h3>A worked example</h3>
          <p>Some policies include an "average" condition. Say your home would cost £300,000 to rebuild, but it's insured for £200,000: two-thirds of its true value.</p>
          <p style="margin-top: 12px;">If a fire then causes £60,000 of damage, an insurer applying average might pay only two-thirds of the claim: <strong>£40,000</strong>, leaving you £20,000 short.</p>
        </aside>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">Protect yourself</span>
            <h2>How to check you're properly insured</h2>
            <p>A few checks at renewal can save a lot of trouble if you ever need to claim.</p>
          </div>
          {arrow_link("claims.html#disputed", "Help with refused or reduced claims")}
        </div>
        <ul class="checklist ticklist">
{mistakes(check_cover)}
        </ul>
      </div>
    </section>""",
        ["a-vs.html", "a-questions.html", "a-glossary.html"],
        image=("homes-terrace", "Victorian terraced houses on a street in Oxford"))

    # ------------------------------------------------------------------ glossary
    glossary = [
        ("Loss adjuster", "A claims specialist appointed and paid by your insurer to investigate a claim and recommend a settlement."),
        ("Loss assessor", "A specialist appointed by you, the policyholder, to prepare, manage and negotiate your claim."),
        ("Policyholder", "The person or business named on the insurance policy."),
        ("Policy schedule", "The document summarising your cover, sums insured and excesses."),
        ("Excess", "The amount you pay towards a claim before your insurer pays the rest."),
        ("Sum insured", "The most your insurer will pay under a section of your policy."),
        ("Underinsurance", "When the sum insured is less than the true cost to rebuild or replace."),
        ("Average", "A policy condition that reduces a claim in proportion when you're underinsured."),
        ("Reinstatement", "Restoring the property to the condition it was in before the loss."),
        ("Escape of water", "Damage caused by water leaking from pipes, tanks or appliances."),
        ("Trace and access", "Cover for finding the source of a leak and repairing the damage caused getting to it."),
        ("Business interruption", "Cover for lost income and extra costs while a business recovers from damage."),
        ("Indemnity period", "The longest period a business interruption policy will pay for after the damage."),
        ("Alternative accommodation", "Temporary housing paid for under your policy while your home can't be lived in."),
        ("Loss of rent", "Cover for rent a landlord loses while a damaged property can't be let."),
        ("Liability", "Your insurer accepting that the loss is covered and that it must pay."),
        ("Proof of ownership", "Evidence that you owned an item, such as receipts, statements or photos."),
        ("Settlement", "The final amount agreed and paid by your insurer."),
    ]
    gl_html = '\n'.join(f'          <div><dt>{t}</dt><dd>{d}</dd></div>' for t, d in glossary)
    article_page(
        "a-glossary.html", "Insurance Claim Glossary | Independent Claims Consultants",
        "Plain-English definitions of insurance claim terms, from loss adjuster and excess to average, trace and access, indemnity period and settlement.",
        "Insurance claim <span>glossary</span>",
        "Plain-English definitions of the words you're likely to hear during your claim.",
        f"""

    <section class="section">
      <div class="container">
        <dl class="glossary">
{gl_html}
        </dl>
      </div>
    </section>""",
        ["a-vs.html", "a-under.html", "a-questions.html"])



def more_guides():
    for g in GUIDES:
        prose = lambda paras: "\n".join(f"            <p>{p}</p>" for p in paras)
        reasons = "\n".join(f"""          <article class="card">
            <h3>{t}</h3>
            <p>{d}</p>
          </article>""" for t, d in g["reasons"])
        body = f"""

    <section class="section">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">{g["intro_eyebrow"]}</span>
            <h2>{g["intro_head"]}</h2>
          </div>
          <div class="prose">
{prose(g["intro"])}
          </div>
        </div>
        <aside class="card">
          {ic("phone", "card-icon")}
          <h3>{g["help_head"]}</h3>
          <div class="prose">
{prose(g["help"])}
          </div>
          <p style="margin-top: 16px;"><a class="btn btn-primary" href="{TEL}">{svg("phone")} Call {PHONE}</a></p>
        </aside>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container">
        <div class="section-head">
          <h2>{g["reasons_head"]}</h2>
        </div>
        <div class="grid-3">
{reasons}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">Step by step</span>
            <h2>{g["steps_head"]}</h2>
            <p>{g["steps_intro"]}</p>
          </div>
        </div>
        <ol class="checklist">
{checklist(g["steps"])}
        </ol>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container">
        <div class="section-head">
          <h2>{g["fos_head"]}</h2>
        </div>
        <div class="prose" style="max-width: 760px;">
{prose(g["fos"])}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">FAQs</span>
            <h2>Common questions</h2>
          </div>
          {arrow_link("faq.html", "See all FAQs")}
        </div>
        <div class="faq">
{faq_items(g["faqs"])}
        </div>
      </div>
    </section>"""
        article_page(
            g["key"], g["title"], g["desc"], g["h1"], g["lead"], body, g["related"], image=g["image"],
            extra_schema=[{
                "@context": "https://schema.org", "@type": "FAQPage",
                "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer",
                                "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a)).strip()}} for q, a in g["faqs"]]}])


# ---------------------------------------------------------------- FAQ

def faq():
    groups = '\n'.join(f"""        <div class="faq-group">
          <h2>{g}</h2>
          <div class="faq">
{faq_items(items)}
          </div>
        </div>""" for g, items in FAQS)
    main = page_hero(
        "FAQs", "Frequently asked <span>questions</span>",
        f'Answers to the questions we\'re asked most often. Can\'t find what you need? Call us on <a href="{TEL}" style="color: var(--accent); font-weight: 600;">{PHONE}</a>.',
        image=("homeowner-woman", "A smiling woman sitting at her laptop at home"))
    main += f"""

    <section class="section">
      <div class="container" style="max-width: 880px;">
{groups}
      </div>
    </section>
{cta()}"""
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a)).strip()}}
            for _, items in FAQS for q, a in items
        ],
    }
    page("faq.html", "Loss Assessor FAQs | Independent Claims Consultants",
         "Answers to common questions about loss assessors, loss adjusters, claim timescales, refused claims, underinsurance and our no win, no fee service.",
         main, schema=schema, crumb="FAQs")


# ---------------------------------------------------------------- contact

def contact():
    who = seg("who", ["Homeowner", "Business", "Landlord"], "c", required=True)
    adjuster = seg("adjuster", ["Yes", "No", "Not sure"], "adj")
    main = page_hero(
        "Start your claim", "Talk to a loss assessor <span>today</span>",
        f'Tell us a little about what\'s happened and we\'ll get back to you with a free, no-obligation assessment. Prefer to talk? Call <a href="{TEL}" style="color: var(--accent); font-weight: 600;">{PHONE}</a>.',
        image=("phone-woman", "A woman talking on the phone at her desk"))
    main += f"""

    <section class="section" style="padding-top: 0;">
      <div class="container contact-layout">
        <form class="form-card" id="claim-form" action="mailto:{EMAIL}?subject=Claim%20enquiry" method="post" enctype="text/plain" novalidate>
          <ol class="wizard-progress">
            <li>About your claim</li>
            <li>Your details</li>
            <li>Check and send</li>
          </ol>

          <div class="panel">
            <h2 tabindex="-1">About your claim</h2>
            <p>This helps us understand how we can help.</p>
            <fieldset class="field">
              <legend>I'm a…</legend>
              {who}
              <p class="field-error">Please choose one.</p>
            </fieldset>
            <div class="field">
              <label for="c-claim">What happened?</label>
              {claim_select("c-claim", required=True, placeholder=True)}
              <p class="field-error">Please choose the type of claim.</p>
            </div>
            <div class="form-row">
              <div class="field">
                <label for="c-date">When did it happen? <span class="hint">(optional)</span></label>
                <input type="date" id="c-date" name="date">
              </div>
              <div class="field">
                <label for="c-postcode">Property postcode <span class="hint">(optional)</span></label>
                <input type="text" id="c-postcode" name="postcode" autocomplete="postal-code">
              </div>
            </div>
            <fieldset class="field">
              <legend>Has your insurer appointed a loss adjuster? <span class="hint">(optional)</span></legend>
              {adjuster}
            </fieldset>
            <div class="field">
              <label for="c-details">Tell us briefly what happened <span class="hint">(optional)</span></label>
              <textarea id="c-details" name="details" placeholder="For example, when it happened, which rooms or areas are affected, and whether you can stay in the property"></textarea>
            </div>
            <div class="wizard-nav">
              <button type="button" class="btn btn-primary" data-next>Next {svg("arrow")}</button>
            </div>
          </div>

          <div class="panel">
            <h2 tabindex="-1">Your details</h2>
            <p>So one of our loss assessors can get in touch.</p>
            <div class="field">
              <label for="c-name">Full name</label>
              <input type="text" id="c-name" name="name" autocomplete="name" required>
              <p class="field-error">Please enter your name.</p>
            </div>
            <div class="form-row">
              <div class="field">
                <label for="c-phone">Phone</label>
                <input type="tel" id="c-phone" name="phone" autocomplete="tel" required>
                <p class="field-error">Please enter a phone number.</p>
              </div>
              <div class="field">
                <label for="c-email">Email</label>
                <input type="email" id="c-email" name="email" autocomplete="email" required>
                <p class="field-error">Please enter a valid email address.</p>
              </div>
            </div>
            <div class="field">
              <label for="c-time">Best time to call</label>
              <select id="c-time" name="time">
                <option>Any time</option>
                <option>Morning</option>
                <option>Afternoon</option>
              </select>
            </div>
            <div class="wizard-nav">
              <button type="button" class="btn btn-ghost" data-back>Back</button>
              <button type="button" class="btn btn-primary" data-next>Next {svg("arrow")}</button>
            </div>
          </div>

          <div class="panel">
            <h2 tabindex="-1">Check and send</h2>
            <p>Check your details, then press send. This opens your email app with your enquiry ready to go.</p>
            <dl class="summary" id="summary"></dl>
            <div class="wizard-nav">
              <button type="button" class="btn btn-ghost" data-back>Back</button>
              <button type="submit" class="btn btn-primary">Send enquiry {svg("arrow")}</button>
            </div>
            <p class="form-note">Or call us on {PHONE}, Monday to Friday, 9am to 5pm.</p>
          </div>

          <div class="panel sent" id="sent">
            {ic("check")}
            <h2 tabindex="-1">Your email is ready to send</h2>
            <p>We've opened your email app with your enquiry filled in. Just press send and we'll be in touch.</p>
            <p>Email app didn't open? Email us at <a href="mailto:{EMAIL}">{EMAIL}</a> or call {PHONE}.</p>
          </div>
        </form>

        <aside class="side">
          <div class="side-card">
            <h3>Contact details</h3>
            <ul class="contact-list">
              <li>{ic("phone")}<a href="{TEL}"><strong>{PHONE}</strong><span>Monday to Friday, 9am to 5pm</span></a></li>
              <li>{ic("mail")}<a href="mailto:{EMAIL}"><strong>{EMAIL}</strong><span>Email us any time</span></a></li>
              <li>{ic("pin")}<div><strong>The Coach House, 3 Brooklands Close</strong><span>Cobham, Surrey KT11 2DR</span></div></li>
            </ul>
          </div>
          <div class="side-card">
            <h3>What happens next</h3>
            <ol class="next-steps">
              <li>We'll contact you to talk through what's happened.</li>
              <li>We arrange your free, no-obligation assessment.</li>
              <li>If you appoint us, your dedicated loss assessor takes over the claim. No win, no fee.</li>
            </ol>
          </div>
          <div class="side-card">
            <h3>Our offices</h3>
            <ul class="contact-list">
              <li>{ic("pin")}<div><strong>Cobham, Surrey</strong><span>Southern office</span></div></li>
              <li>{ic("pin")}<div><strong>Hale, Manchester</strong><span>Head office</span></div></li>
            </ul>
          </div>
        </aside>
      </div>
    </section>"""
    page("contact.html", "Contact Our Loss Assessors | Independent Claims Consultants",
         "Contact our Southern office in Cobham, Surrey for a free, no-obligation assessment of your insurance claim. Call 0161 904 7800 or start your claim online.",
         main, page_css="""
    @media (max-width: 768px) { body { padding-bottom: 0; } }""", callbar=False, crumb="Contact")


# ---------------------------------------------------------------- claim-type and audience pages

def contact_link(who=None, claim=None):
    params = []
    if who:
        params.append("who=" + quote(who))
    if claim:
        params.append("claim=" + quote(claim))
    return "contact.html" + ("?" + "&amp;".join(params) if params else "")


def service_page(s):
    quick = "\n        <ul class=\"creds\">" + "".join(
        f"<li><strong>{a}</strong><span>{b}</span></li>" for a, b in QUICK) + "</ul>"
    start = contact_link(s.get("who"), s.get("claim"))
    intro = "\n".join(f"            <p>{p}</p>" for p in s["intro"])
    help_html = mini_grid(s["help"])
    covers = "\n".join(f"            <li><div><strong>{a}</strong><span>{b}</span></div></li>" for a, b in s["covers"])
    cases = "\n".join(f"""          <article class="card">
            <p class="case-meta">{CASES[i][0]}</p>
            <h3>{CASES[i][1]}</h3>
            <p>{CASES[i][2]}</p>
          </article>""" for i in s["cases"])
    related = "\n".join(
        f'          <a class="tile" href="{k}">{ic(CARD[k][0])}<strong>{CARD[k][1]}</strong><span>{CARD[k][2]}</span></a>'
        for k in s["related"])
    advice = ""
    if s.get("advice"):
        href, text = s["advice"]
        advice = f'\n        <p class="note">{svg("info")}<span><strong>Need help right now?</strong> <a href="{href}">{text}</a>.</span></p>'

    main = page_hero(s["pill"], s["h1"], s["lead"], quick, image=s["image"])
    main += f"""

    <section class="section">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">Independent loss assessors</span>
            <h2>{s["intro_head"]}</h2>
          </div>
          <div class="prose">
{intro}
          </div>
        </div>
        <aside class="side-card">
          <h3>Talk to a loss assessor</h3>
          <p style="margin-bottom: 18px; color: var(--muted);">Get a free, no-obligation assessment of your claim. No win, no fee.</p>
          <a href="{start}" class="btn btn-primary" style="width: 100%;">Start your claim {svg("arrow")}</a>
          <ul class="contact-list" style="margin-top: 20px;">
            <li>{ic("phone")}<a href="{TEL}"><strong>{PHONE}</strong><span>Monday to Friday, 9am to 5pm</span></a></li>
            <li>{ic("mail")}<a href="mailto:{EMAIL}"><strong>Email us</strong><span>We'll get back to you</span></a></li>
          </ul>
        </aside>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">How we help</span>
          <h2>{s["help_head"]}</h2>
        </div>
        <div class="mini-grid three">
{help_html}
        </div>{advice}
      </div>
    </section>

    <section class="section">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">Your claim</span>
            <h2>{s["covers_head"]}</h2>
            <p>{s["covers_intro"]}</p>
          </div>
          {arrow_link(start, "Start your claim")}
        </div>
        <ul class="checklist ticklist">
{covers}
        </ul>
      </div>
    </section>"""
    if cases:
        main += f"""

    <section class="section section-soft">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Recent cases</span>
          <h2>How we've helped clients</h2>
        </div>
        <div class="grid-2">
{cases}
        </div>
      </div>
    </section>"""
    main += f"""

    <section class="section{'' if cases else ' section-soft'}">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">FAQs</span>
            <h2>Common questions</h2>
          </div>
          {arrow_link("faq.html", "See all FAQs")}
        </div>
        <div class="faq">
{faq_items(s["faqs"])}
        </div>
      </div>
    </section>

    <section class="section{' section-soft' if cases else ''}">
      <div class="container">
        <div class="head-row">
          <div class="section-head">
            <span class="eyebrow">Related claims</span>
            <h2>Other ways we can help</h2>
          </div>
          {arrow_link("claims.html", "All claims we handle")}
        </div>
        <div class="grid-4">
{related}
        </div>
      </div>
    </section>
{cta()}"""

    schema = [
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "serviceType": s["service_type"],
            "name": s["crumb"],
            "description": s["desc"],
            "url": SITE + "/" + s["route"],
            "areaServed": {"@type": "Country", "name": "United Kingdom"},
            "provider": {"@type": "ProfessionalService", "name": "Independent Claims Consultants",
                         "url": SITE + "/", "telephone": "+44 161 904 7800"},
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a)).strip()}}
                for q, a in s["faqs"]
            ],
        },
    ]
    page(s["key"], s["title"], s["desc"], main, schema=schema, crumb=s["crumb"],
         crumb_parent=("claims.html", "Claims we handle"))


# ---------------------------------------------------------------- Surrey (Southern office)

SURREY_AREAS = [
    "Cobham", "Esher", "Weybridge", "Walton-on-Thames", "Leatherhead", "Woking", "Guildford", "Epsom",
    "Kingston upon Thames", "Dorking", "Godalming", "Staines-upon-Thames", "Chertsey", "Camberley", "Farnham", "Reigate",
]

SURREY_FAQS = [
    ("Do you cover my part of Surrey?",
     f"<p>Our Southern office in Cobham works with clients across Surrey and the surrounding areas. If you're not sure whether we cover your town, call us on {PHONE} and we'll let you know.</p>"),
    ("Will a loss assessor visit my property?",
     "<p>Yes. Your loss assessor will inspect the damage, review your policy and, where it helps your claim, meet your insurer's loss adjuster at the property.</p>"),
]


def surrey():
    team = [
        ("AM", "Andrew MacInnes", "Loss Assessor",
         "\"Every client is assigned a dedicated loss assessor. Their experience will ensure your claim is run smoothly and efficiently.\""),
        ("NM", "Neil Munnerley", "Loss Assessor",
         "One of our dedicated loss assessors, managing claims for homeowners, landlords and businesses from first visit to final settlement."),
    ]
    team_html = '\n'.join(f"""          <article class="card member">
            <span class="avatar" aria-hidden="true">{i}</span>
            <h3>{n}</h3>
            <p class="role">{r}</p>
            <p class="office">{svg("pin")}Southern office, Cobham</p>
            <p>{q}</p>
          </article>""" for i, n, r, q in team)

    claims = [
        ("flood", "Flood", "Parts of Surrey lie close to the Thames, the Wey and the Mole, and homes near these rivers have flooded in wet winters such as 2013–14. We manage flood claims from drying out to final settlement.", "flood.html"),
        ("droplet", "Escape of water", "Burst pipes and leaks are among the most common home insurance claims, and older properties can hide damage under floors and behind walls. We make sure all of it is found and claimed for.", "escape.html"),
        ("fire", "Fire and smoke", "From kitchen fires to serious house fires, we guide you through every decision and make sure smoke and soot damage is fully included in your claim.", "fire.html"),
        ("storm", "Storm damage", "High winds and falling trees can damage roofs, walls and contents. We arrange emergency works and present a complete claim for the damage.", "storm.html"),
        ("briefcase", "Business interruption", "For Surrey businesses, our forensic and consequential loss accountants calculate your lost income while your premises are restored.", "bi.html"),
        ("key", "Landlord claims", "If a let property is damaged, we handle the claim and the reinstatement, and claim for the rent you lose while it can't be let.", "landlords.html"),
    ]
    claims_html = '\n'.join(f"""          <article class="card">
            {ic(i, "card-icon")}
            <h3>{t}</h3>
            <p>{p}</p>
            {arrow_link(href, "Find out more")}
          </article>""" for i, t, p, href in claims)

    areas_html = ''.join(f'<li>{a}</li>' for a in SURREY_AREAS)
    faqs = SURREY_FAQS + [faq_lookup(q) for q in ["When should I contact a loss assessor?", "How much do you charge?"]]
    maps = "https://www.google.com/maps/search/?api=1&query=" + "The+Coach+House+3+Brooklands+Close+Cobham+KT11+2DR"

    quick = """
        <ul class="creds">
          <li><strong>Southern office</strong><span>The Coach House, Cobham, Surrey</span></li>
          <li><strong>Local loss assessors</strong><span>Andrew MacInnes and Neil Munnerley</span></li>
          <li><strong>No win, no fee</strong><span>Free, no-obligation assessment</span></li>
        </ul>"""
    main = page_hero(
        "Southern office · Cobham, Surrey", "Loss assessors <span>in Surrey</span>",
        "Our Southern office in Cobham helps homeowners, landlords and businesses across Surrey and the South with fire, flood and other insurance claims. We work for you, not your insurer.",
        quick, image=("surrey-shere", "Historic cottages on a village street in Shere, Surrey"))
    main += f"""

    <section class="section">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">Local and independent</span>
            <h2>A local loss assessor on your side</h2>
          </div>
          <div class="prose">
            <p>When a fire, flood or escape of water damages your property, your insurer appoints a loss adjuster to assess the claim on its behalf. Our loss assessors work for you instead, preparing and negotiating your claim so you receive everything you're entitled to.</p>
            <p>Being based in Cobham means your loss assessor is close at hand to inspect the damage, meet your insurer's loss adjuster at the property and keep an eye on the repairs as they progress.</p>
            <p>Our Southern office is part of Independent Claims Consultants, which has managed insurance claims for more than 30 years, with our head office in Hale, Cheshire.</p>
          </div>
        </div>
        <aside class="side-card">
          <h3>Our Southern office</h3>
          <ul class="contact-list">
            <li>{ic("pin")}<div><strong>The Coach House, 3 Brooklands Close</strong><span>Cobham, Surrey KT11 2DR</span></div></li>
            <li>{ic("phone")}<a href="{TEL}"><strong>{PHONE}</strong><span>Monday to Friday, 9am to 5pm</span></a></li>
            <li>{ic("mail")}<a href="mailto:{EMAIL}"><strong>{EMAIL}</strong><span>Email us any time</span></a></li>
          </ul>
          <p style="margin-top: 20px;"><a class="link-arrow" href="{maps}" target="_blank" rel="noopener">Get directions {svg("arrow")}</a></p>
        </aside>
      </div>
    </section>

    <section class="section section-soft" id="areas">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Areas we cover</span>
          <h2>Helping clients across Surrey</h2>
          <p>From our office in Cobham we work with homeowners, landlords and businesses throughout Surrey and the surrounding areas, including:</p>
        </div>
        <ul class="areas">{areas_html}</ul>
        <p class="note">{svg("info")}<span>Not sure if we cover your area? Call us on <a href="{TEL}"><strong>{PHONE}</strong></a> and we'll let you know.</span></p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Claims we handle</span>
          <h2>Common claims we help with in Surrey</h2>
        </div>
        <div class="grid-3">
{claims_html}
        </div>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container">
        <div class="head-row">
          <div class="section-head">
            <span class="eyebrow">Your local team</span>
            <h2>Meet our Southern office loss assessors</h2>
          </div>
          {arrow_link("about.html#team", "Meet the whole team")}
        </div>
        <div class="grid-2">
{team_html}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">FAQs</span>
            <h2>Questions from Surrey clients</h2>
            <p>Quick answers to what people in Surrey ask us most.</p>
          </div>
          {arrow_link("faq.html", "See all FAQs")}
        </div>
        <div class="faq">
{faq_items(faqs)}
        </div>
      </div>
    </section>
{cta("Talk to a loss assessor in Surrey", "Get your first consultation free with our Southern office team. No win, no fee.")}"""

    schema = [
        {
            "@context": "https://schema.org",
            "@type": "ProfessionalService",
            "name": "Independent Claims Consultants – Southern Office",
            "url": SITE + "/" + ROUTES["surrey.html"],
            "image": SITE + "/assets/img/og-image.jpg",
            "telephone": "+44 161 904 7800",
            "email": EMAIL,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "The Coach House, 3 Brooklands Close",
                "addressLocality": "Cobham",
                "addressRegion": "Surrey",
                "postalCode": "KT11 2DR",
                "addressCountry": "GB",
            },
            "openingHours": "Mo-Fr 09:00-17:00",
            "areaServed": [{"@type": "Place", "name": f"{a}, Surrey"} for a in SURREY_AREAS[:6]] + [{"@type": "AdministrativeArea", "name": "Surrey"}],
            "parentOrganization": {"@type": "Organization", "name": "Independent Claims Consultants", "url": SITE + "/"},
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a)).strip()}}
                for q, a in faqs
            ],
        },
    ]
    page("surrey.html", "Loss Assessors in Surrey | Independent Claims Consultants",
         "Independent loss assessors in Cobham, Surrey, helping homeowners, landlords and businesses with fire, flood and escape of water claims. No win, no fee.",
         main, schema=schema, crumb="Loss assessors in Surrey")


# ---------------------------------------------------------------- Manchester & Cheshire (head office)

MANCHESTER_AREAS = [
    "Manchester", "Salford", "Trafford", "Altrincham", "Hale", "Sale", "Stockport", "Cheadle",
    "Wilmslow", "Knutsford", "Macclesfield", "Warrington", "Bolton", "Wigan", "Oldham", "Chester",
]


def manchester():
    ROUTES["manchester.html"] = "loss-assessors-manchester/"
    team = [
        ("NC", "Nic Castleton", "Managing Director",
         "\"Your specialist loss assessor will ensure your claim is processed as quickly as possible, with everything in place ready for the moment liability is accepted.\""),
        ("NH", "Nigel Hennerley", "Loss Assessor",
         "\"You will have peace of mind knowing your loss assessor will guide you through the entire claims process.\""),
    ]
    team_html = '\n'.join(f"""          <article class="card member">
            <span class="avatar" aria-hidden="true">{i}</span>
            <h3>{n}</h3>
            <p class="role">{r}</p>
            <p class="office">{svg("pin")}Head office, Hale</p>
            <p>{q}</p>
          </article>""" for i, n, r, q in team)
    claims = [
        ("flood", "Flood", "Greater Manchester has seen serious flooding in recent years, including the Boxing Day floods of 2015 and Storm Christoph in 2021. We manage flood claims from drying out to final settlement.", "flood.html"),
        ("droplet", "Escape of water", "Burst pipes and leaks are among the most common home insurance claims, and older terraced and Victorian properties can hide damage under floors and behind walls.", "escape.html"),
        ("fire", "Fire and smoke", "From kitchen fires to serious house fires, we guide you through every decision and make sure smoke and soot damage is fully included in your claim.", "fire.html"),
        ("storm", "Storm damage", "High winds and heavy rain can damage roofs, chimneys and walls. We arrange emergency works and challenge unfair wear and tear decisions.", "storm.html"),
        ("briefcase", "Business interruption", "For businesses across the region, our forensic and consequential loss accountants calculate lost income while your premises are restored.", "bi.html"),
        ("key", "Landlord claims", "If a let property is damaged, we handle the claim and the reinstatement, and claim for the rent you lose while it can't be let.", "landlords.html"),
    ]
    claims_html = '\n'.join(f"""          <article class="card">
            {ic(i, "card-icon")}
            <h3>{t}</h3>
            <p>{p}</p>
            {arrow_link(href, "Find out more")}
          </article>""" for i, t, p, href in claims)
    areas_html = ''.join(f'<li>{a}</li>' for a in MANCHESTER_AREAS)
    local_faqs = [
        ("Do you cover my part of Greater Manchester or Cheshire?",
         f"<p>Our head office in Hale works with clients across Greater Manchester, Cheshire and the surrounding areas. If you're not sure whether we cover your town, call us on {PHONE} and we'll let you know.</p>"),
        ("Will a loss assessor visit my property?",
         "<p>Yes. Your loss assessor will inspect the damage, review your policy and, where it helps your claim, meet your insurer's loss adjuster at the property.</p>"),
    ]
    faqs = local_faqs + [faq_lookup(q) for q in ["When should I contact a loss assessor?", "How much do you charge?"]]
    case = CASES[3]
    maps = "https://www.google.com/maps/search/?api=1&query=" + "Arco+House+86+Woburn+Drive+Hale+WA15+8NE"
    quick = """
        <ul class="creds">
          <li><strong>Head office</strong><span>Arco House, Hale, near Altrincham</span></li>
          <li><strong>Local loss assessors</strong><span>Nic Castleton and Nigel Hennerley</span></li>
          <li><strong>No win, no fee</strong><span>Free, no-obligation assessment</span></li>
        </ul>"""
    main = page_hero(
        "Head office · Hale, Cheshire", "Loss assessors <span>in Manchester and Cheshire</span>",
        "Our head office in Hale helps homeowners, landlords and businesses across Greater Manchester and Cheshire with fire, flood and other insurance claims. We work for you, not your insurer.",
        quick, image=("manchester-street", "A Manchester street with Victorian buildings and modern towers"))
    main += f"""

    <section class="section">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">Local and independent</span>
            <h2>Your local loss assessors in the North West</h2>
          </div>
          <div class="prose">
            <p>When a fire, flood or escape of water damages your property, your insurer appoints a loss adjuster to assess the claim on its behalf. Our loss assessors work for you instead, preparing and negotiating your claim so you receive everything you're entitled to.</p>
            <p>Independent Claims Consultants has managed insurance claims for more than 30 years, and our head office is in Hale, near Altrincham. Being close by means your loss assessor can inspect the damage, meet your insurer's loss adjuster at the property and keep an eye on the repairs.</p>
            <p>Our team is led by Managing Director Nic Castleton, whose family has worked in loss assessment for over 100 years and helped establish the Institute of Public Loss Assessors.</p>
          </div>
        </div>
        <aside class="side-card">
          <h3>Our head office</h3>
          <ul class="contact-list">
            <li>{ic("pin")}<div><strong>Arco House, 86 Woburn Drive</strong><span>Hale, Altrincham, Cheshire WA15 8NE</span></div></li>
            <li>{ic("phone")}<a href="{TEL}"><strong>{PHONE}</strong><span>Monday to Friday, 9am to 5pm</span></a></li>
            <li>{ic("mail")}<a href="mailto:{EMAIL}"><strong>{EMAIL}</strong><span>Email us any time</span></a></li>
          </ul>
          <p style="margin-top: 20px;"><a class="link-arrow" href="{maps}" target="_blank" rel="noopener">Get directions {svg("arrow")}</a></p>
        </aside>
      </div>
    </section>

    <section class="section section-soft" id="areas">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Areas we cover</span>
          <h2>Helping clients across Greater Manchester and Cheshire</h2>
          <p>From our head office in Hale we work with homeowners, landlords and businesses throughout the region, including:</p>
        </div>
        <ul class="areas">{areas_html}</ul>
        <p class="note">{svg("info")}<span>Not sure if we cover your area? Call us on <a href="{TEL}"><strong>{PHONE}</strong></a> and we'll let you know.</span></p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Claims we handle</span>
          <h2>Common claims we help with in the North West</h2>
        </div>
        <div class="grid-3">
{claims_html}
        </div>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">A local case</span>
            <h2>Back home after a house fire in Manchester</h2>
          </div>
          {arrow_link("fire.html", "Fire damage claims")}
        </div>
        <article class="card">
          <p class="case-meta">{case[0]}</p>
          <h3>{case[1]}</h3>
          <p>{case[2]}</p>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="head-row">
          <div class="section-head">
            <span class="eyebrow">Your local team</span>
            <h2>Meet our head office team</h2>
          </div>
          {arrow_link("about.html#team", "Meet the whole team")}
        </div>
        <div class="grid-2">
{team_html}
        </div>
      </div>
    </section>

    <section class="section section-soft">
      <div class="container split top">
        <div>
          <div class="section-head">
            <span class="eyebrow">FAQs</span>
            <h2>Questions from local clients</h2>
          </div>
          {arrow_link("faq.html", "See all FAQs")}
        </div>
        <div class="faq">
{faq_items(faqs)}
        </div>
      </div>
    </section>
{cta("Talk to a loss assessor in the North West", "Get your first consultation free with our head office team. No win, no fee.")}"""
    schema = [
        {
            "@context": "https://schema.org",
            "@type": "ProfessionalService",
            "name": "Independent Claims Consultants – Head Office",
            "url": SITE + "/" + ROUTES["manchester.html"],
            "image": SITE + "/assets/img/og-image.jpg",
            "telephone": "+44 161 904 7800",
            "email": EMAIL,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Arco House, 86 Woburn Drive",
                "addressLocality": "Hale, Altrincham",
                "addressRegion": "Cheshire",
                "postalCode": "WA15 8NE",
                "addressCountry": "GB",
            },
            "openingHours": "Mo-Fr 09:00-17:00",
            "areaServed": [{"@type": "AdministrativeArea", "name": "Greater Manchester"},
                           {"@type": "AdministrativeArea", "name": "Cheshire"}],
            "parentOrganization": {"@type": "Organization", "name": "Independent Claims Consultants", "url": SITE + "/"},
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a)).strip()}}
                for q, a in faqs
            ],
        },
    ]
    page("manchester.html", "Loss Assessors in Manchester &amp; Cheshire | Independent Claims Consultants",
         "Independent loss assessors with a head office in Hale, Cheshire, helping clients across Greater Manchester and Cheshire with fire and flood claims. No win, no fee.",
         main, schema=schema, crumb="Loss assessors in Manchester and Cheshire")


# ---------------------------------------------------------------- 404, redirects, sitemap, robots

def not_found():
    main = page_hero(
        "Page not found", "Sorry, we can't find <span>that page</span>",
        "The page may have moved when we updated our website. Try one of these instead, or call us if you need help with a claim.",
        "")
    main += f"""

    <section class="section" style="padding-top: 0;">
      <div class="container">
        <div class="grid-3">
          <article class="card">{ic("home", "card-icon")}<h3>Homepage</h3><p>Start again from our homepage.</p>{arrow_link("index.html", "Go to the homepage")}</article>
          <article class="card">{ic("file", "card-icon")}<h3>Claims we handle</h3><p>Fire, flood, escape of water and more.</p>{arrow_link("claims.html", "See claim types")}</article>
          <article class="card">{ic("phone", "card-icon")}<h3>Start your claim</h3><p>Get a free, no-obligation assessment.</p>{arrow_link("contact.html", "Contact us")}</article>
        </div>
      </div>
    </section>"""
    page("404.html", "Page Not Found | Independent Claims Consultants",
         "The page you were looking for could not be found.", main, prefix="/", indexable=False)


def redirect_stubs():
    """Static redirect pages for old addresses. They work on any host, including GitHub Pages."""
    lines = ["# Permanent redirects for hosts that read a _redirects file (Netlify, Cloudflare Pages).",
             "# The matching HTML redirect pages are a fallback for hosts that don't."]
    for old, new in REDIRECTS.items():
        target = SITE + "/" + new.split("#")[0]
        rel = (link_prefix(old if old.endswith("/") else "") + new) or "./"
        stub = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="UTF-8">
  <title>Page moved | Independent Claims Consultants</title>
  <link rel="canonical" href="{target}">
  <meta http-equiv="refresh" content="0; url={rel}">
  <script>location.replace({json.dumps(rel.split("#")[0])} + (location.search || "") + ({json.dumps("#" + rel.split("#")[1]) if "#" in rel else "location.hash"}));</script>
</head>
<body>
  <p>This page has moved. <a href="{rel}">Continue to the new page</a>.</p>
</body>
</html>
"""
        out = ROOT / (old + "index.html" if old.endswith("/") else old)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(stub)
        lines.append(f"/{old}  /{new}  301!")
        if old.endswith("/"):
            lines.append(f"/{old[:-1]}  /{new}  301!")
    (ROOT / "_redirects").write_text("\n".join(lines) + "\n")


def sitemap_and_robots():
    today = __import__("datetime").date.today().isoformat()
    urls = "\n".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in SITEMAP)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    home()
    claims()
    about()
    advice()
    more_guides()
    faq()
    contact()
    surrey()
    manchester()
    for s in SERVICE_PAGES:
        service_page(s)
    not_found()
    redirect_stubs()
    sitemap_and_robots()
    print(f"Built {len(SITEMAP)} pages, a 404 page and {len(REDIRECTS)} redirects")
