const { app, BrowserWindow } = require('electron');

function createWindow () {
  // Create the browser window.
  let win = new BrowserWindow({
    width: 1304,
    height: 864,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: true
    }
  });

  // and load the index.html of the app.
  win.loadFile('build/index.html');
}

app.on('ready', createWindow);
