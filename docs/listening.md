# Listening to a knowledge base

Every knowledge base published with Glassdocs can be listened to as well as read. There are two ways to hear a page, and they sit side by side in the site's own header:

- **▶ Listen** reads the page with a speech voice already installed on the reader's device. It is on every page of every Glassdocs KB, needs no extension and no setup, and makes no network request at all.
- **▶ AI** plays a narration generated ahead of time with a neural voice. It appears only on pages that have a current one.

Generating the AI narration is an admin task, described in [Generating AI narration](#generating-ai-narration) below. Listening needs nothing from the reader.

## Listening to a page

The controls sit in the page header, next to the light/dark toggle. On a narrow screen the word "Listen" is dropped and only the ▶ glyph shows, to keep the header usable on a phone.

### ▶ Listen

This is browser speech synthesis. The reader's own browser and operating system produce the audio, using a voice installed on the device.

- It is present on **every published page**, and no repo variable, plan, or setting can turn it off. It is not affected by the `AUDIO_ENABLED` variable that governs AI narration.
- It works with **no extension installed**, which is what makes it reach phones. iOS Safari and Android Chrome cannot run a browser extension, but they can do this.
- It reads the article and nothing else. Code blocks are skipped, headings get a pause, and the navigation, sidebar and "¶" permalink anchors are never spoken.
- If the device has no on-device voice, the control still renders, greyed out, and says why. It never falls back to a cloud speech service, because a private KB's text is not something to hand to a synthesis vendor the reader never chose.

There is no variable to switch it off, since there is nothing to save by switching it off. A KB that does not want the control on brand grounds can hide it from its own stylesheet:

```css
/* docs/stylesheets/extra.css, referenced from extra_css in mkdocs.yml */
#glassdocs-read-aloud { display: none; }
```

### ▶ AI

The AI button appears only when the page carries a narration that was generated from **the version of the page you are looking at**.

The published page records the source revision it was built from, and each clip records the revision it was generated from. When those disagree, the clip is stale and the button is not rendered at all. In practice: edit a page and redeploy, and its ▶ AI disappears until someone regenerates it. There is no "this narration may be out of date" state for readers to misread, and a stale clip is never played.

A clip covers the whole page as a single recording. It is served in Ogg Opus, and on a browser that cannot play that container the button is not shown.

### The player

Once something is playing, a ▾ appears beside the controls and opens a player. What it offers depends on which source is playing, because the two know different things about their own position:

| | ▶ Listen | ▶ AI |
| --- | --- | --- |
| Progress | Share of the page read, plus an estimate of time remaining | Elapsed and total time, as a clock |
| Seeking | Jump to any section from the list | Click anywhere on the progress bar |
| Skip buttons | Previous and next sentence | Back and forward 10 seconds |
| "Now", "Coming up" and "Read" | Yes, with the current sentence quoted and upcoming sections listed | No, because a clip is one continuous recording |

Stop lives inside the player. Pressing Escape or clicking outside closes the player without stopping playback, and leaving the page stops it.

Every control is a real button, so the player is reachable by keyboard and its labels are exposed to screen readers. The one exception worth knowing: the progress bar is operated by pointer only. Keyboard users can still skip, and can jump between sections from the list.

### What listening sends

This is the part worth stating precisely, because a knowledge base is often private.

- **▶ Listen makes no network request whatsoever.** Not when the page loads, not when you press play, not when it finishes. The audio is produced by your own browser and operating system.
- **▶ AI makes exactly one request, and only when you press it**: a GET for the audio file that the page itself names, on the KB's own address, behind whatever Access gate already protects the site. The clip is not preloaded, so a page you never press play on fetches nothing.
- **Nothing is sent to Glassdocs.** No analytics, no telemetry, no identifier, no page text. The question "does this page have a narration?" is answered by two meta tags in the HTML you already downloaded, never by asking a server.

One honest limit, which the control's own wording respects: no browser API reports which voice actually spoke. Glassdocs asks for a voice the browser marks as on-device and pins that voice on every utterance, so the request is unambiguous. The claim is about what is asked for, not a guarantee about where every operating system ultimately produced the sound.

## Generating AI narration

AI narration is produced in the admin console at [app.glassdocs.site/admin](https://app.glassdocs.site/admin/), under **Audio**. You need to be an admin of the GitHub org, the same as everywhere else in the console.

**The speech model runs on your own machine**, in your browser, in WebAssembly. There is no inference API and no third-party speech service anywhere in the path. [Privacy, precisely](#privacy-precisely) below sets out exactly what moves where.

### Turn it on for the KB first

Audio publishing is off by default and is enabled per KB with a GitHub Actions **repository variable** on the KB repo:

| Variable | Value | Effect |
| --- | --- | --- |
| `AUDIO_ENABLED` | exactly `true` | Clips generated for this KB are published with the site, and readers get ▶ AI on pages that have a current one |

Set it on the KB repo under **Settings → Secrets and variables → Actions → Variables**. The console does not set it for you.

!!! warning "The value must be the literal string `true`"
    `1`, `yes`, `TRUE` and an empty value all count as off. A deploy that finds one of those says so in its log rather than guessing. With the variable off, the deploy is byte for byte what it was before: no audio directory, no manifest, nothing for a reader to click. ▶ Listen is unaffected either way.

The console skips pages belonging to a KB whose variable is not set, so turn it on before generating rather than after.

### The run

1. **Choose what to generate.** Every knowledge base, one KB, only pages that have no audio yet, or a set of pages you tick individually.
2. **Download the voice model**, once. It is about 93 MB and downloads only when you click the button, never in the background. It is cached afterwards, so later runs download nothing.
3. **Press "Estimate and queue…".** This reads each selected page and counts its spoken words, then tells you how many pages, how many words, roughly how much audio that is, and roughly how long the machine will take. Accept it and the pages join the queue.
4. **Press "Start generating".** Progress shows the page in flight, the chunk within it, and time remaining for both the page and the batch.

### It is slow, and that is the trade

Synthesis runs at roughly 3.8 seconds of computation per second of audio, on one CPU core. A 900-word page takes about 23 minutes. A few hundred pages is a multi-day job.

That is the cost of not sending your documents to a speech vendor, and it is the same on every plan, free included. There is no faster paid tier, because there is no server-side generation to sell. The estimate calibrates to your actual machine after the first page, so the number you see gets more accurate as the run goes on.

Practical consequences:

- **The tab has to stay open and visible.** The console asks the browser to keep the screen awake, and tells you if the browser refuses. Closing the lid or quitting still stops it.
- **Closing the tab loses at most the page in flight.** Everything else stays queued. Reopen the Audio section and the button reads "Resume", with the number of pages left.
- **Pause is durable and shared.** It survives a reload and applies to everyone in the org, not just your tab.
- **Two admins can generate at once.** The queue is server-side, so two tabs take different pages rather than duplicating work.

### Browser requirements

Generation needs a browser that can encode Opus through WebCodecs: **Chrome 94+, Firefox 130+, or Safari 16.4+**. A browser that cannot is told so plainly rather than being allowed to produce something unplayable. No GPU is required.

### Publishing the clips

Clips are stored as assets on a GitHub Release tagged `glassdocs-audio` **in your own KB repo**. Glassdocs does not keep them.

They reach readers on the KB's **next deploy**: the publisher pulls the release assets into the built site, stamps each page with the clip it owns, and the ▶ AI button appears. Generating audio does not itself trigger a deploy, so push a change or press **Redeploy** in the console when you want the clips to go live. You can preview any clip from the console's inventory before it is published.

If a clip cannot be fetched at deploy time, the deploy still succeeds and publishes the site without audio. A documentation deploy blocked by a missing narration would be the worse failure.

## Privacy, precisely

For readers:

- ▶ Listen makes no network request at all.
- ▶ AI fetches one file from your own site, only on a press.
- Nothing about what a reader is reading reaches Glassdocs.

For the admin generating audio:

- **Synthesis happens on your machine**, in your browser. No inference service, no model host, and no other third party is involved.
- **Page text is never uploaded from your browser, never stored by Glassdocs, and never sent to a third party.** It is read from your GitHub repo and passed through the Glassdocs API to your browser, in the same passthrough way [editing](how-it-works.md#editing-two-paths-both-passthrough) works. It is not written to Glassdocs storage at any point.
- **Only the finished audio is uploaded**, and it goes straight through to a GitHub Release on your own repo. Even failures report a code from a fixed list rather than a message, so a failing sentence cannot leak in an error string.
- **The voice model is downloaded from Glassdocs' own storage**, not from a third-party model host.
- What Glassdocs keeps is the work list: which pages are queued, which are done, and which repo they belong to. Never text, never audio.

## Related pages

- [Admin dashboard](admin.md) — where the Audio section lives.
- [Publishing](publishing.md) — the deploy that carries the clips to the site.
- [Security and privacy](security.md) — the zero-data model these guarantees come from.
- [Browser extension](extension.md) — reading and editing pages, with its own read-aloud in a newer release.
