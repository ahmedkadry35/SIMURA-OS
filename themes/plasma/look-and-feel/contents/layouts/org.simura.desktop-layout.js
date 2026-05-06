// SIMURA OS — default Plasma desktop layout (Win11-style).
//
// Plasma reads this JavaScript file at first login (via the Look-and-Feel
// package) and uses it to construct the user's panels and widgets.
//
// Layout shape:
//   - No top panel.
//   - One single floating panel at the bottom-center, fitted to its content,
//     containing: SIMURA "S" launcher · pinned task icons · system tray ·
//     digital clock · power/user.
//   - Wallpaper applied to all virtual desktops.
//
// Reference:
//   https://develop.kde.org/docs/plasma/scripting/

var plasma = getApiVersion(1);

// Wipe any existing panels (idempotent re-runs).
var allPanels = panels();
for (var i = 0; i < allPanels.length; ++i) {
    allPanels[i].remove();
}

// ===========================================================================
// Single floating panel: bottom, centered, fitted to content (Win11 dock-style).
// ===========================================================================
var dock = new Panel("org.kde.panel");
dock.location   = "bottom";
dock.height     = 56;
dock.floating   = true;
dock.lengthMode = "fit";        // shrink to fit widgets
dock.alignment  = "center";     // center on screen
dock.hiding     = "normalpanel"; // visible by default; user can switch to autohide

// --- SIMURA "S" launcher (kickoff) ---
var launcher = dock.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "simura-logo");
launcher.writeConfig("favoritesPortedToKAstats", true);
// Wide layout so the menu has room for the pinned/recommended grid.
launcher.writeConfig("compactView", false);
launcher.writeConfig("primaryActions", 0);
launcher.writeConfig("alphaSort", true);
launcher.writeConfig("favoritesDisplay", 0);
launcher.writeConfig("applicationsDisplay", 0);
launcher.writeConfig("menuLabel", "");
launcher.writeConfig("paneSwap", false);
launcher.writeConfig("showActionButtonCaptions", true);
// Default "Pinned" set — Win11-style first row of common apps.
launcher.writeConfig("favoriteApps",
    "applications:simura-assistant.desktop," +
    "applications:firefox.desktop," +
    "applications:org.kde.dolphin.desktop," +
    "applications:org.kde.konsole.desktop," +
    "applications:org.kde.discover.desktop," +
    "applications:org.kde.kate.desktop," +
    "applications:org.kde.kcalc.desktop," +
    "applications:org.kde.systemsettings.desktop," +
    "applications:libreoffice-writer.desktop," +
    "applications:libreoffice-calc.desktop," +
    "applications:libreoffice-impress.desktop," +
    "applications:org.kde.spectacle.desktop");

// --- Pinned tasks (icon-only, like Win11 taskbar items) ---
var iconTasks = dock.addWidget("org.kde.plasma.icontasks");
iconTasks.currentConfigGroup = ["General"];
iconTasks.writeConfig("launchers",
    "applications:simura-assistant.desktop," +
    "applications:org.kde.dolphin.desktop," +
    "applications:firefox.desktop," +
    "applications:org.kde.konsole.desktop," +
    "applications:org.kde.discover.desktop," +
    "applications:org.kde.kate.desktop," +
    "applications:libreoffice-writer.desktop," +
    "applications:org.kde.spectacle.desktop," +
    "applications:org.kde.systemsettings.desktop");
iconTasks.writeConfig("showOnlyCurrentDesktop", false);
iconTasks.writeConfig("showOnlyCurrentScreen", false);
iconTasks.writeConfig("showOnlyCurrentActivity", true);
iconTasks.writeConfig("groupingStrategy", 0);
iconTasks.writeConfig("indicateAudioStreams", true);
iconTasks.writeConfig("iconSize", 1);

// --- Tiny separator before tray ---
dock.addWidget("org.kde.plasma.marginsseparator");

// --- System tray (network, sound, bluetooth, …) ---
dock.addWidget("org.kde.plasma.systemtray");

// --- Digital clock with date below time ---
var clock = dock.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("autoFontAndSize", false);
clock.writeConfig("fontFamily", "Roboto");
clock.writeConfig("dateFormat", "shortDate");
clock.writeConfig("dateDisplayFormat", "BesideTime");
clock.writeConfig("showDate", true);
clock.writeConfig("use24hFormat", 1);

// --- User switcher / power button ---
dock.addWidget("org.kde.plasma.userswitcher");

// ===========================================================================
// Wallpaper on all virtual desktops.
// ===========================================================================
var allDesktops = desktops();
for (var i = 0; i < allDesktops.length; ++i) {
    var d = allDesktops[i];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "/usr/share/wallpapers/SIMURA/contents/images/3840x2160.png");
    d.writeConfig("FillMode", 2); // 2 = scaled-and-cropped
}
