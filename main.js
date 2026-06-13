// main.js — Electron entry point for Shabbir's 30-Day Gauntlet
// Run with: npx electron . (from this folder in VS Code terminal)

const { app, BrowserWindow, Tray, Menu, shell, session } = require('electron')
const path = require('path')
const fs   = require('fs')

let mainWindow
let tray
let alwaysOnTop = true

// ── Icon paths ────────────────────────────────────────────────────────────
const ICON_PATH      = path.join(__dirname, 'icon.png')
const TRAY_ICON_PATH = path.join(__dirname, 'tray-icon.png')

// ── Tray ──────────────────────────────────────────────────────────────────
function buildTrayMenu() {
  return Menu.buildFromTemplate([
    {
      label: 'Show Gauntlet',
      click: () => { mainWindow.show(); mainWindow.focus() },
    },
    {
      label: 'Always on Top',
      type: 'checkbox',
      checked: alwaysOnTop,
      click: (item) => {
        alwaysOnTop = item.checked
        mainWindow.setAlwaysOnTop(alwaysOnTop)
        tray.setContextMenu(buildTrayMenu())
      },
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => { app.isQuitting = true; app.quit() },
    },
  ])
}

function createTray() {
  const iconFile = fs.existsSync(TRAY_ICON_PATH) ? TRAY_ICON_PATH : ICON_PATH
  tray = new Tray(iconFile)
  tray.setToolTip("Shabbir's 30-Day Gauntlet")
  tray.setContextMenu(buildTrayMenu())

  // Left-click → show / focus window
  tray.on('click', () => {
    if (!mainWindow) return
    if (mainWindow.isVisible()) {
      mainWindow.focus()
    } else {
      mainWindow.show()
      mainWindow.focus()
    }
  })
}

// ── Main window ───────────────────────────────────────────────────────────
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 850,
    minWidth: 900,
    minHeight: 600,
    title: "Shabbir's 30-Day Gauntlet",
    backgroundColor: '#0a0a0a',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    icon: fs.existsSync(ICON_PATH) ? ICON_PATH : undefined,
    alwaysOnTop,          // stays visible over other apps
    skipTaskbar: false,   // keep it in the taskbar while visible
  })

  mainWindow.loadFile('shabbir_30day_gauntlet.html')
  mainWindow.setMenuBarVisibility(false)

  // Open external links in the real browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  // Minimize → hide to tray (removes it from taskbar too)
  mainWindow.on('minimize', () => {
    mainWindow.hide()
  })

  // Close button → hide to tray instead of quitting
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault()
      mainWindow.hide()
    }
  })

  mainWindow.on('closed', () => { mainWindow = null })
}

// ── App lifecycle ─────────────────────────────────────────────────────────
app.isQuitting = false

app.whenReady().then(() => {
  // Grant microphone permission so the voice coach works without a popup
  session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
    const allowed = ['media', 'microphone', 'audioCapture']
    callback(allowed.includes(permission))
  })
  session.defaultSession.setPermissionCheckHandler((webContents, permission) => {
    return ['media', 'microphone', 'audioCapture'].includes(permission)
  })

  createWindow()
  createTray()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('before-quit', () => { app.isQuitting = true })

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
