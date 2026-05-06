/*
 *  SIMURA OS — Calamares slideshow shown during the install.
 *  Three frames cycling on a 6s timer.
 */
import QtQuick 2.15
import calamares.slideshow 1.0

Presentation {
    id: presentation

    Timer {
        interval: 6000
        running:  presentation.activatedInCalamares
        repeat:   true
        onTriggered: presentation.goToNextSlide()
    }

    Slide {
        Image { source: "logo.png"; anchors.centerIn: parent; width: 220; height: 220 }
        Text {
            anchors { top: parent.verticalCenter; topMargin: 130; horizontalCenter: parent.horizontalCenter }
            text: "Welcome to SIMURA OS"
            color: "#00e5ff"
            font { family: "Roboto"; pointSize: 28; weight: Font.Bold }
        }
        Text {
            anchors { top: parent.verticalCenter; topMargin: 180; horizontalCenter: parent.horizontalCenter }
            text: "Built on Arch Linux + KDE Plasma · Powered by your AI assistant"
            color: "#e6f1ff"
            font { family: "Roboto"; pointSize: 14 }
        }
    }

    Slide {
        Text {
            anchors.centerIn: parent
            text: "Your AI is local."
            color: "#00e5ff"
            font { family: "Roboto"; pointSize: 36; weight: Font.Bold }
        }
        Text {
            anchors { top: parent.verticalCenter; topMargin: 60; horizontalCenter: parent.horizontalCenter }
            text: "SIMURA Assistant runs entirely on your hardware via Ollama.\nNo API keys, no telemetry, no cloud round-trip."
            color: "#e6f1ff"
            horizontalAlignment: Text.AlignHCenter
            font { family: "Roboto"; pointSize: 14 }
        }
    }

    Slide {
        Text {
            anchors.centerIn: parent
            text: "Tuned for speed."
            color: "#00e5ff"
            font { family: "Roboto"; pointSize: 36; weight: Font.Bold }
        }
        Text {
            anchors { top: parent.verticalCenter; topMargin: 60; horizontalCenter: parent.horizontalCenter }
            text: "zram, earlyoom, BBR, performance governor on AC,\nschedutil on battery — sane defaults out of the box."
            color: "#e6f1ff"
            horizontalAlignment: Text.AlignHCenter
            font { family: "Roboto"; pointSize: 14 }
        }
    }

    function onActivate()   { /* no-op */ }
    function onLeave()      { /* no-op */ }
}
