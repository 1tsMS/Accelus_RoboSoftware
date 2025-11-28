window.addEventListener('DOMContentLoaded', () => {
  window.workspace = Blockly.inject('blocklyDiv', {
    toolbox: ROBOT_TOOLBOX_XML,
    media: 'node_modules/blockly/media/',
    trashcan: true,
    zoom: {
      controls: true,
      wheel: true,
      startScale: 1.0,
      maxScale: 3,
      minScale: 0.3,
      scaleSpeed: 1.2,
    },
    move: {
      scrollbars: true,
      drag: true,
      wheel: true,
    },
    renderer: 'zelos',
    theme: Blockly.Themes.Classic
  });

  const runButton = document.getElementById('runButton');
  const toggleCodeButton = document.getElementById('toggleCodeButton');
  const saveCodeButton = document.getElementById('saveCodeButton'); // ✅ Grab Save button
  const codePanel = document.getElementById('codePanel');
  const codeArea = document.getElementById('codeArea');

  function updateCode() {
    const code = Blockly.Python.workspaceToCode(workspace);
    codeArea.textContent = code || "# (no code yet)";
  }

  runButton.addEventListener('click', () => {
    const code = Blockly.Python.workspaceToCode(workspace);
    if (pyBridge) {
      pyBridge.receiveCode(code); // Sends code to Python
    }
  });

  toggleCodeButton.addEventListener('click', () => {
    if (codePanel.style.display === 'none') {
      updateCode();
      codePanel.style.display = 'flex';
      toggleCodeButton.textContent = "Hide Code";
    } else {
      codePanel.style.display = 'none';
      toggleCodeButton.textContent = "Show Code";
    }
  });

  // ✅ Save code button sends code to Python for saving
  saveCodeButton.addEventListener('click', () => {
    const code = Blockly.Python.workspaceToCode(workspace);
    if (pyBridge) {
      pyBridge.receiveCode(code);
      alert("Code saved to file via Python!");
    }
  });

  // Auto-update code when blocks change (only if panel is open)
  workspace.addChangeListener(() => {
    if (codePanel.style.display === 'flex') {
      updateCode();
    }
  });
});
