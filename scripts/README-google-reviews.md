# Automatic Google reviews updater (not active)

This branch prepares a daily GitHub Action that refreshes trimoco.com's
Google rating, review count, on-page review cards, AggregateRating, and
Review schema from the Places API (New). **Do not merge it to `main`
until Ackeme has added a Google Places API key.** Scheduled workflows
only run from the default branch, and the job no-ops if the secret is
missing.

## What Ackeme needs to provide

1. A Google Cloud project **he owns**, with billing enabled (required even
   for free-tier usage).
2. The **Places API (New)** enabled on that project.
3. An API key restricted to Places API (New). Do not commit the key.
   Add it as the GitHub Actions repository secret `GOOGLE_PLACES_API_KEY`
   on `Okapi2255/trimoco-site` (Settings → Secrets and variables → Actions).
4. Optional: if Render autodeploy is off, create a Render deploy hook for
   `trimoco-site` (`srv-dbk2c5e7bikc738ubvd0`) and add it as the repository
   secret `RENDER_DEPLOY_HOOK_URL`. As of 17 Nov 2026 the service has
   `autoDeploy=yes` (trigger: commit) on `main`, so a hook is only needed
   if that is turned off. Recent production deploys were still triggered
   via the Render API, so confirm autodeploy actually fires before relying
   on it alone.

After the secret is in place, merge this branch to `main` (or enable the
workflow there). Nothing in this folder prints or writes the key.

## What the job does

- Daily at 11:20 UTC (6:20 AM ET during EST), or on manual `workflow_dispatch`.
- `GET https://places.googleapis.com/v1/places/ChIJ__8beJpkwokRkhfKdrDJYuM`
  with field mask `rating,userRatingCount,reviews`.
- Writes `public/data/google-reviews.json`.
- Updates the visible rating/count, the "See all N reviews on Google"
  link, review cards (at most 5; Places does not return more),
  AggregateRating on every LocalBusiness block, and Review schema only
  for reviews actually shown on the page.
- Commits and pushes only when something changed.
- Leaves Lynbrook mentions and street addresses untouched.

## Cost (one call per day)

Requesting `reviews` bills the call at **Place Details Enterprise +
Atmosphere** (SKU `EB23-5ECC-F753`): **1,000 free requests per month**,
then $25 per 1,000 (1,001–100,000). One call per day is about 30–31
calls a month, so the expected cost is **$0 / month**, inside the free
allowance. A billing account is still required.

Sources:

- [Google Maps Platform core services pricing list](https://developers.google.com/maps/billing-and-pricing/pricing)
- [Place Data Fields (New)](https://developers.google.com/maps/documentation/places/web-service/data-fields)
  (`reviews` is Enterprise + Atmosphere; `rating` and `userRatingCount`
  alone are Place Details Enterprise).
