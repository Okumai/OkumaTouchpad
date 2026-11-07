pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Hyprland
import qs.Ui as Ui
import qs.Commons as Commons

Item {
    id: root
    property var shell: null
    readonly property string pluginId: "okuma.dev_touchpad4omarchy"
    // Resolve each helper URL directly: Qt.resolvedUrl(".") need not end in '/'.
    function localFile(name) {
        return decodeURIComponent(Qt.resolvedUrl(name).toString().replace(/^file:\/\//, ""));
    }
    readonly property string panelFont: shell && shell.bar ? shell.bar.fontFamily : Commons.Style.font.family
    readonly property color foreground: Commons.Color.foreground
    property bool opened: false
    property var draft: ({})
    property var fields: []
    property string output: ""
    property string operation: ""
    property string resultState: "unknown"
    property string statusMessage: ""
    property string launcherMessage: ""
    property bool dirty: false
    property string selectedGroup: "Touchpad"
    readonly property var groups: ["Touchpad", "Workspaces", "Vertical swipes", "Pinch", "Integration"]
    readonly property bool busy: worker.running
    Commons.Translations { id: strings; directory: Qt.resolvedUrl("i18n") }
    // Omarchy's git installer does not run install.py or other repository hooks.
    // Register only the application entry on enable/load; never apply input settings.
    Component.onCompleted: launcherWorker.running = true
    Process {
        id: launcherWorker
        command: ["python3", root.localFile("launcher.py"), "install"]
        property string errors: ""
        stderr: StdioCollector { onStreamFinished: launcherWorker.errors = text }
        onExited: (exitCode, exitStatus) => {
            if (exitCode !== 0 || exitStatus !== 0) {
                root.launcherMessage = strings.t("launcherFailed") + "\n" + errors;
                console.warn("OkumaTouchpad launcher registration failed: " + errors);
            }
        }
    }

    component PanelText: Text {
        color: root.foreground
        font.family: root.panelFont
        font.pixelSize: Commons.Style.font.body
        textFormat: Text.PlainText
        wrapMode: Text.WordWrap
    }
    component Action: Ui.Button {
        fontFamily: root.panelFont
        fontSize: Commons.Style.font.body
        foreground: root.foreground
        focusable: true
    }
    function open(payloadJson) {
        const monitor = Hyprland.focusedMonitor;
        panel.screen = Quickshell.screens.find(s => monitor && s.name === monitor.name) || Quickshell.screens[0];
        opened = true;
        if (!dirty && !busy) execute("describe");
        Qt.callLater(() => content.forceActiveFocus());
    }
    function close() { opened = false; }
    function status() { return opened ? "open" : "closed"; }
    function diagnostics() {
        return JSON.stringify({opened: opened, busy: busy, dirty: dirty, fieldCount: fields.length,
            settings: draft, operation: operation, output: output, resultState: resultState,
            statusMessage: statusMessage, launcherMessage: launcherMessage,
            geometry: {screenHeight: panel.height, cardHeight: card.height, top: card.y,
                bottom: panel.height - card.y - card.height}, selectedGroup: selectedGroup});
    }
    function dismiss() { close(); if (shell) shell.hide(pluginId); }
    function setDraft(key, value) {
        const next = Object.assign({}, draft);
        next[key] = value;
        draft = next;
        dirty = true;
        resultState = "draft";
        statusMessage = strings.t("unsaved");
    }
    function execute(action) {
        if (busy) return;
        operation = action;
        output = "";
        if (action === "apply") {
            resultState = "working";
            statusMessage = strings.t("working");
        }
        let args = ["python3", localFile("touchpad.py"), action];
        if (action === "apply" || action === "preview")
            args = args.concat(["--settings-json", JSON.stringify(draft)]);
        worker.command = args;
        worker.running = true;
    }
    Process {
        id: worker
        property string result: ""
        property string errors: ""
        onStarted: { result = ""; errors = ""; }
        stdout: StdioCollector { onStreamFinished: worker.result = text }
        stderr: StdioCollector { onStreamFinished: worker.errors = text }
        onExited: (exitCode, exitStatus) => {
            const succeeded = exitCode === 0 && exitStatus === 0;
            if (root.operation === "describe" && succeeded) {
                try {
                    const data = JSON.parse(result);
                    root.draft = data.settings;
                    root.fields = data.fields;
                    root.output = data.warnings.join("\n");
                    root.dirty = false;
                    root.resultState = data.status.applied ? "applied" : "inactive";
                    root.statusMessage = data.status.message;
                } catch (error) {
                    root.resultState = "failed";
                    root.statusMessage = strings.t("readFailed");
                    root.output = String(error);
                }
            } else {
                root.output = result + (errors ? "\n" + errors : "");
                if (!succeeded) {
                    root.resultState = "failed";
                    root.statusMessage = root.operation === "apply" ? strings.t("applyFailed") : strings.t("operationFailed");
                    if (!root.output.trim()) root.output = "Helper exited with code " + exitCode + ", status " + exitStatus;
                } else if (root.operation === "apply") {
                    root.dirty = false;
                    root.resultState = "applied";
                    root.statusMessage = strings.t("applySucceeded");
                }
            }
        }
    }
    PanelWindow {
        id: panel
        visible: root.opened
        anchors { top: true; bottom: true; left: true; right: true }
        exclusionMode: ExclusionMode.Ignore
        color: "transparent"
        WlrLayershell.namespace: "okuma-touchpad"
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.keyboardFocus: root.opened ? WlrKeyboardFocus.Exclusive : WlrKeyboardFocus.None
        // Logical pixels: reserve symmetric space for both the bar and dock.
        readonly property real barSize: root.shell && root.shell.bar
            ? root.shell.bar.barSize : Commons.Style.space(32)
        readonly property real safeMargin: Math.max(Commons.Style.space(80), barSize + Commons.Style.space(40), height * 0.10)
        MouseArea { anchors.fill: parent; onClicked: root.dismiss() }
        Ui.BorderSurface {
            id: card
            anchors.centerIn: parent
            width: Math.max(1, Math.min(Commons.Style.space(760), panel.width - Commons.Style.space(48)))
            height: Math.max(1, Math.min(Commons.Style.space(740), panel.height - panel.safeMargin * 2))
            color: Commons.Color.popups.background
            borderSpec: Commons.Border.surfaceSpec("popups", "border", Commons.Color.popups.border, Math.max(1, Commons.Style.space(2)))
            radius: Commons.Style.cornerRadius
            LayoutMirroring.enabled: Commons.I18n.rightToLeft
            LayoutMirroring.childrenInherit: true
            MouseArea { anchors.fill: parent }
            ColumnLayout {
                id: content
                anchors.fill: parent
                anchors.margins: Commons.Style.space(22)
                spacing: Commons.Style.space(12)
                focus: true
                Keys.onEscapePressed: root.dismiss()
                PanelText {
                    Layout.fillWidth: true
                    text: strings.t("title")
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: Commons.Style.font.title
                }
                PanelText {
                    Layout.fillWidth: true
                    text: strings.t("intro")
                    horizontalAlignment: Text.AlignHCenter
                    opacity: 0.65
                    font.pixelSize: Commons.Style.font.bodySmall
                }
                Ui.PanelSeparator { Layout.fillWidth: true }
                Flow {
                    Layout.fillWidth: true
                    Layout.preferredHeight: implicitHeight
                    spacing: Commons.Style.space(4)
                    Repeater {
                        model: root.groups
                        delegate: Action {
                            required property string modelData
                            text: strings.t("group." + modelData)
                            selected: root.selectedGroup === modelData
                            onClicked: { root.selectedGroup = modelData; scroll.contentY = 0; }
                        }
                    }
                }
                Flickable {
                    id: scroll
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    contentWidth: width
                    contentHeight: settingsColumn.implicitHeight
                    clip: true
                    boundsBehavior: Flickable.StopAtBounds
                    Controls.ScrollBar.vertical: Controls.ScrollBar { policy: Controls.ScrollBar.AsNeeded }
                    Column {
                        id: settingsColumn
                        width: scroll.width - Commons.Style.space(12)
                        spacing: Commons.Style.space(10)
                        Repeater {
                            model: root.fields.filter(f => f.group === root.selectedGroup)
                            delegate: Column {
                                id: settingRow
                                required property var modelData
                                width: settingsColumn.width
                                spacing: Commons.Style.space(6)
                                Loader {
                                    width: parent.width
                                    sourceComponent: settingRow.modelData.kind === "boolean" ? booleanEditor : valueEditor
                                }
                                Component {
                                    id: booleanEditor
                                    Ui.Toggle {
                                        label: strings.t("setting." + settingRow.modelData.key)
                                        fontFamily: root.panelFont
                                        titleSize: Commons.Style.font.body
                                        checked: root.draft[settingRow.modelData.key] === true
                                        enabled: !root.busy
                                        onClicked: root.setDraft(settingRow.modelData.key, !checked)
                                    }
                                }
                                Component {
                                    id: valueEditor
                                    Column {
                                        spacing: Commons.Style.space(6)
                                        PanelText {
                                            width: parent.width
                                            text: strings.t("setting." + settingRow.modelData.key)
                                        }
                                        Loader {
                                            width: parent.width
                                            sourceComponent: settingRow.modelData.kind === "enum" ? enumEditor : textEditor
                                        }
                                    }
                                }
                                Component {
                                    id: enumEditor
                                    Ui.Dropdown {
                                        value: String(root.draft[settingRow.modelData.key])
                                        options: settingRow.modelData.choices.map(v => ({value: String(v), label: String(v)}))
                                        fontFamily: root.panelFont
                                        enabled: !root.busy
                                        onChanged: value => root.setDraft(settingRow.modelData.key,
                                            typeof settingRow.modelData.default === "number" ? Number(value) : value)
                                    }
                                }
                                Component {
                                    id: textEditor
                                    Ui.TextField {
                                        text: String(root.draft[settingRow.modelData.key])
                                        font.family: root.panelFont
                                        enabled: !root.busy
                                        selectByMouse: true
                                        onTextEdited: root.setDraft(settingRow.modelData.key,
                                            settingRow.modelData.kind === "number" ? Number(text) : text)
                                    }
                                }
                                PanelText {
                                    visible: settingRow.modelData.kind === "number"
                                    width: parent.width
                                    opacity: 0.65
                                    font.pixelSize: Commons.Style.font.bodySmall
                                    text: visible ? strings.t("range").arg(settingRow.modelData.minimum).arg(settingRow.modelData.maximum) : ""
                                }
                            }
                        }
                    }
                }
                Ui.PanelSeparator { Layout.fillWidth: true }
                PanelText {
                    Layout.fillWidth: true
                    text: root.busy ? strings.t("working") : root.statusMessage || strings.t("explicit")
                    font.bold: root.resultState === "failed" || root.resultState === "inactive"
                    font.pixelSize: Commons.Style.font.bodySmall
                }
                PanelText {
                    Layout.fillWidth: true
                    visible: root.launcherMessage !== ""
                    text: root.launcherMessage
                    font.pixelSize: Commons.Style.font.bodySmall
                }
                Flow {
                    Layout.fillWidth: true
                    Layout.preferredHeight: implicitHeight
                    spacing: Commons.Style.space(4)
                    Action { text: strings.t("preview"); enabled: !root.busy && root.fields.length > 0; onClicked: root.execute("preview") }
                    Action { text: strings.t("apply"); selected: root.dirty; enabled: !root.busy && root.fields.length > 0; onClicked: root.execute("apply") }
                    Action { text: strings.t("reload"); enabled: !root.busy; onClicked: root.execute("describe") }
                    Action { text: strings.t("doctor"); enabled: !root.busy; onClicked: root.execute("doctor") }
                    Action { text: strings.t("close"); onClicked: root.dismiss() }
                }
                Controls.ScrollView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.min(Commons.Style.space(100), card.height * 0.15)
                    clip: true
                    Controls.TextArea {
                        text: root.output
                        textFormat: TextEdit.PlainText
                        color: root.foreground
                        readOnly: true
                        selectByMouse: true
                        wrapMode: TextEdit.Wrap
                        font.family: root.panelFont
                        font.pixelSize: Commons.Style.font.bodySmall
                        background: Item {}
                    }
                }
            }
        }
    }
}
