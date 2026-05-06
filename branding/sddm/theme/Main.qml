/*
 *  SIMURA OS — SDDM login theme (Qt Quick / QML).
 *  A minimal, futuristic login screen: dark gradient background, soft
 *  cyan glow behind the logo, single username/password field, a small
 *  session selector and a power menu in the corner.
 */
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#000814"

    LayoutMirroring.enabled: Qt.locale().textDirection == Qt.RightToLeft
    LayoutMirroring.childrenInherit: true

    TextConstants { id: textConstants }

    // Subtle radial brand glow behind the logo
    Rectangle {
        id: glow
        anchors.centerIn: parent
        width: parent.width * 0.6
        height: width
        radius: width / 2
        color: "transparent"
        opacity: 0.25
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#00e5ff" }
            GradientStop { position: 1.0; color: "#00000000" }
        }
    }

    // Centered SIMURA logo
    Image {
        id: logo
        source: "logo.png"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: -180
        width: 196
        height: 196
        smooth: true
        antialiasing: true
    }

    Text {
        id: title
        anchors.top: logo.bottom
        anchors.topMargin: 24
        anchors.horizontalCenter: parent.horizontalCenter
        text: "SIMURA OS"
        color: "#00e5ff"
        font.family: "Roboto"
        font.pixelSize: 36
        font.letterSpacing: 6
    }

    // Login card
    Rectangle {
        id: card
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: title.bottom
        anchors.topMargin: 48
        width: 420
        height: 240
        radius: 16
        color: "#0a0e2a"
        border.color: "#00e5ff"
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 28
            spacing: 16

            ComboBox {
                id: userCombo
                Layout.fillWidth: true
                model: userModel
                textRole: "name"
                currentIndex: userModel.lastIndex
            }

            TextField {
                id: passwordField
                Layout.fillWidth: true
                placeholderText: textConstants.password
                echoMode: TextInput.Password
                font.family: "Roboto"
                onAccepted: sddm.login(userCombo.currentText, text, sessionCombo.currentIndex)
                Keys.onReturnPressed: sddm.login(userCombo.currentText, text, sessionCombo.currentIndex)
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                ComboBox {
                    id: sessionCombo
                    Layout.fillWidth: true
                    model: sessionModel
                    textRole: "name"
                    currentIndex: sessionModel.lastIndex
                }

                Button {
                    id: loginButton
                    text: textConstants.login
                    onClicked: sddm.login(userCombo.currentText, passwordField.text, sessionCombo.currentIndex)
                }
            }
        }
    }

    // Bottom-right power menu
    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 24
        spacing: 16

        Button { text: textConstants.suspend; onClicked: sddm.suspend() }
        Button { text: textConstants.reboot;  onClicked: sddm.reboot()  }
        Button { text: textConstants.shutdown; onClicked: sddm.powerOff() }
    }

    // Bottom-left clock
    Text {
        id: clock
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 24
        color: "#7a8aa6"
        font.family: "JetBrains Mono"
        font.pixelSize: 14
        text: Qt.formatDateTime(new Date(), "ddd dd MMM  hh:mm")
        Timer { interval: 1000; running: true; repeat: true
            onTriggered: clock.text = Qt.formatDateTime(new Date(), "ddd dd MMM  hh:mm") }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            passwordField.text = ""
            passwordField.focus = true
        }
    }

    Component.onCompleted: passwordField.focus = true
}
