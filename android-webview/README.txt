════════════════════════════════════════════════════════════════════════
  ANDROID APK SETUP — Microphone access for the Gauntlet voice coaches
════════════════════════════════════════════════════════════════════════

Your HTML voice coaches no longer use the browser's webkitSpeechRecognition
(which does NOT work inside an Android WebView). They now record audio with
MediaRecorder and send it to Gemini, which transcribes AND analyses your real
pronunciation. For that to work, the APK must:
  (a) hold the RECORD_AUDIO permission, and
  (b) grant the WebView's microphone request, and
  (c) serve the page from a SECURE origin (handled by WebViewAssetLoader).

The 3 files/edits below do exactly that.

────────────────────────────────────────────────────────────────────────
STEP 1 — Put the HTML in the assets folder, renamed to index.html
────────────────────────────────────────────────────────────────────────
Copy shabbir_30day_gauntlet.html into:

    app/src/main/assets/index.html

(Create the "assets" folder if it doesn't exist:
 right-click app  →  New  →  Folder  →  Assets Folder.)

────────────────────────────────────────────────────────────────────────
STEP 2 — AndroidManifest.xml
────────────────────────────────────────────────────────────────────────
Add these three lines INSIDE <manifest> but ABOVE <application>:

    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.RECORD_AUDIO"/>
    <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS"/>

(INTERNET is required for the Gemini API calls; RECORD_AUDIO for the mic.)

────────────────────────────────────────────────────────────────────────
STEP 3 — app/build.gradle  (Module: app)  → dependencies { ... }
────────────────────────────────────────────────────────────────────────
Add:

    implementation "androidx.webkit:webkit:1.11.0"
    implementation "androidx.appcompat:appcompat:1.7.0"

Then click "Sync Now".

────────────────────────────────────────────────────────────────────────
STEP 4 — MainActivity.kt
────────────────────────────────────────────────────────────────────────
Replace your MainActivity.kt with the one in this folder.
⚠ Change the very first line `package com.shabbir.gauntlet` to match the
  package name already at the top of YOUR existing MainActivity.kt.

────────────────────────────────────────────────────────────────────────
STEP 5 — Build & run
────────────────────────────────────────────────────────────────────────
Build the APK, install on your phone, open the app:
  • On first launch you'll get the Android "Allow microphone?" dialog → Allow.
  • Open Spanish or Accent coach → hold the 🎤 button → speak → release.
  • If it was denied, the in-app "Enable Microphone" button explains how to
    re-enable it in the phone's app settings.

════════════════════════════════════════════════════════════════════════
  WHAT THIS DOES NOT DO — overlay over other apps
════════════════════════════════════════════════════════════════════════
A floating window that stays on top AFTER you leave the app needs a whole
native Android feature: the SYSTEM_ALERT_WINDOW permission plus a foreground
Service drawing with WindowManager. It cannot be driven from the HTML and is
a substantial separate piece of native code. It is intentionally NOT included
here. Ask if you actually want it and it can be built as a follow-up.

════════════════════════════════════════════════════════════════════════
  FALLBACK — if your project has no AppCompat / androidx.webkit
════════════════════════════════════════════════════════════════════════
You can load file:///android_asset/index.html with a plain WebView + the same
onPermissionRequest() grant, but the mic is unreliable from a file:// origin
on some devices. The WebViewAssetLoader approach above is the reliable one.
