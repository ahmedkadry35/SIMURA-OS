// SIMURA OS — default Plasma desktop layout.
//
// Plasma reads this JavaScript file at first login (via the Look-and-Feel
// package) and uses it to construct the user's panels and widgets.
// Reference:
//   https://develop.kde.org/docs/plasma/scripting/

var plasma = getApiVersion(1);

// Wipe any existing panels (idempotent re-runs)
var allPanels = panels();
for (var i = 0; i < allPanels.length; ++i) {
    allPanels[i].remove();
}

// === Top panel: launcher + system tray + clock + AI assistant button ====
var topPanel = new Panel("org.kde.panel");
topPanel.location = "top";
topPanel.height   = 36;
topPanel.floating = true;

// Application launcher (kickoff)
var launcher = topPanel.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "simura-logo");
launcher.writeConfig("favoritesPortedToKAstats", true);

// Pinned tasks
var iconTasks = topPanel.addWidget("org.kde.plasma.icontasks");
iconTasks.currentConfigGroup = ["General"];
iconTasks.writeConfig("launchers",
    "applications:firefox.desktop," +
    "applications:org.kde.dolphin.desktop," +
    "applications:org.kde.konsole.desktop," +
    "applications:simura-assistant.desktop," +
    "applications:org.kde.discover.desktop," +
    "applications:org.kde.kate.desktop");

// Spacer pushes following items to the right
topPanel.addWidget("org.kde.plasma.panelspacer");

// System tray + clock + power
topPanel.addWidget("org.kde.plasma.systemtray");
topPanel.addWidget("org.kde.plasma.digitalclock");
topPanel.addWidget("org.kde.plasma.userswitcher");

// === Bottom dock: minimal app dock with auto-hide ========================
var dock = new Panel("org.kde.panel");
dock.location = "bottom";
dock.height   = 56;
dock.floating = true;
dock.lengthMode = "fit";
dock.alignment  = "center";
dock.hiding     = "autohide";

var dockTasks = dock.addWidget("org.kde.plasma.icontasks");
dockTasks.currentConfigGroup = ["General"];
dockTasks.writeConfig("launchers",
    "applications:simura-assistant.desktop," +
    "applications:org.kde.dolphin.desktop," +
    "applications:firefox.desktop," +
    "applications:org.kde.konsole.desktop," +
    "applications:org.kde.discover.desktop," +
    "applications:org.kde.kate.desktop," +
    "applications:org.kde.spectacle.desktop," +
    "applications:org.kde.systemsettings.desktop");
dockTasks.writeConfig("showOnlyCurrentDesktop", false);
dockTasks.writeConfig("groupingStrategy", 0);

// Apply the SIMURA wallpaper to all virtual desktops.
var allDesktops = desktops();
for (var i = 0; i < allDesktops.length; ++i) {
    var d = allDesktops[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "/usr/share/wallpapers/SIMURA/contents/images/3840x2160.png");
    d.writeConfig("FillMode", 2); // scaled-and-cropped
}
