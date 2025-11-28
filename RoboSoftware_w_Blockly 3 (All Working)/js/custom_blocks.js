Blockly.defineBlocksWithJsonArray([
  {
    "type": "robot_move",
    "message0": "move arm to X: %1 Y: %2 Z: %3",
    "args0": [
      { "type": "field_number", "name": "X", "value": 0 },
      { "type": "field_number", "name": "Y", "value": 0 },
      { "type": "field_number", "name": "Z", "value": 0 }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 230,
    "tooltip": "Move to coordinates",
    "helpUrl": ""
  },
  {
    "type": "robot_rotate",
    "message0": "rotate joint %1 by %2°",
    "args0": [
      {
        "type": "field_dropdown",
        "name": "JOINT",
        "options": [
          ["base","BASE"],
          ["shoulder","SHOULDER"],
          ["elbow","ELBOW"],
          ["wrist","WRIST"]
        ]
      },
      { "type": "field_angle", "name": "ANGLE", "angle": 90 }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Rotate a joint",
    "helpUrl": ""
  },
  {
    "type": "robot_set_angle",
    "message0": "set joint %1 to %2°",
    "args0": [
      {
        "type": "field_dropdown",
        "name": "JOINT",
        "options": [
          ["base","BASE"],
          ["shoulder","SHOULDER"],
          ["elbow","ELBOW"],
          ["wrist","WRIST"]
        ]
      },
      { "type": "field_angle", "name": "ANGLE", "angle": 0 }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Set joint to absolute angle",
    "helpUrl": ""
  },
  {
    "type": "robot_set_all_angles",
    "message0": "set all joints base: %1 shoulder: %2 elbow: %3 wrist: %4",
    "args0": [
      { "type": "field_angle", "name": "BASE", "angle": 0 },
      { "type": "field_angle", "name": "SHOULDER", "angle": 0 },
      { "type": "field_angle", "name": "ELBOW", "angle": 0 },
      { "type": "field_angle", "name": "WRIST", "angle": 0 }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 200,
    "tooltip": "Set all joints to specific angles",
    "helpUrl": ""
  },
  {
    "type": "robot_record_position",
    "message0": "record current position as %1",
    "args0": [
      { "type": "field_variable", "name": "POS", "variable": "pos1" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 290,
    "tooltip": "Record current position to a variable",
    "helpUrl": ""
  },
  {
    "type": "robot_move_to_recorded",
    "message0": "move to recorded position %1",
    "args0": [
      { "type": "field_variable", "name": "POS", "variable": "pos1" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 290,
    "tooltip": "Move arm to previously recorded position",
    "helpUrl": ""
  },
  {
    "type": "robot_grip",
    "message0": "grip",
    "previousStatement": null,
    "nextStatement": null,
    "colour": 20,
    "tooltip": "Close gripper",
    "helpUrl": ""
  },
  {
    "type": "robot_release",
    "message0": "release",
    "previousStatement": null,
    "nextStatement": null,
    "colour": 20,
    "tooltip": "Open gripper",
    "helpUrl": ""
  }
]);

/* =======================
   Python Generators
   ======================= */
Blockly.Python['robot_move'] = function(block) {
  return `move_to(${block.getFieldValue('X')}, ${block.getFieldValue('Y')}, ${block.getFieldValue('Z')})\n`;
};

Blockly.Python['robot_rotate'] = function(block) {
  return `rotate("${block.getFieldValue('JOINT').toLowerCase()}", ${block.getFieldValue('ANGLE')})\n`;
};

Blockly.Python['robot_set_angle'] = function(block) {
  return `set_angle("${block.getFieldValue('JOINT').toLowerCase()}", ${block.getFieldValue('ANGLE')})\n`;
};

Blockly.Python['robot_set_all_angles'] = function(block) {
  return `set_all_angles(${block.getFieldValue('BASE')}, ${block.getFieldValue('SHOULDER')}, ${block.getFieldValue('ELBOW')}, ${block.getFieldValue('WRIST')})\n`;
};

Blockly.Python['robot_record_position'] = function(block) {
  const pos = Blockly.Python.variableDB_.getName(block.getFieldValue('POS'), Blockly.Variables.NAME_TYPE);
  return `${pos} = record_position()\n`;
};

Blockly.Python['robot_move_to_recorded'] = function(block) {
  const pos = Blockly.Python.variableDB_.getName(block.getFieldValue('POS'), Blockly.Variables.NAME_TYPE);
  return `move_to_recorded(${pos})\n`;
};

Blockly.Python['robot_grip'] = () => 'grip()\n';
Blockly.Python['robot_release'] = () => 'release()\n';
