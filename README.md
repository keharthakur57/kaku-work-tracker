# KAKU WORK TRACKER

Mobile-first PWA for Kehar Singh's attendance, production and performance tracking.
Data lives in his Google Sheet "KAKU Personal Attendance & Performance Management".

- App: https://keharthakur57.github.io/kaku-work-tracker/
- Preview with sample data: add `?demo=1` (no data is saved, sync disabled).

## Security model (honest summary)

- The site is a PUBLIC static page. Its password gate is device-local only: a
  salted, stretched hash stored in the browser. It stops casual snooping on a
  shared phone, but it is NOT server-side authentication and the page itself is
  public. Anyone who opens the URL sees the gate, not the data; that is all it
  guarantees.
- The sync secret is created by the backend (`kwtProvision()`, owner-only) and
  is shown once. It lives in the browser's session storage by default; the
  "keep on this device" option stores it in localStorage, which is less safe.
- The Apps Script backend validates every field, rate-limits, and rejects
  replayed requests. The web app URL is still public with a shared secret:
  treat the secret like a password.

## Backend setup (owner)

1. Sheet -> Extensions -> Apps Script, paste `apps-script/Code.gs`, save.
2. Run `kwtProvision` once (editor). Copy the secret from the execution log.
3. Deploy -> New deployment -> Web app. Execute as: Me. Access: Anyone.
4. App Settings: paste URL + secret, Test connection, then Sync now.
