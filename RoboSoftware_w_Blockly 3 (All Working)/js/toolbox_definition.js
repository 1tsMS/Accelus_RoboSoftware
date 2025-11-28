const ROBOT_TOOLBOX_XML = `
<xml id="toolbox" style="display: none">
  <category name="Movement" colour="#5C81A6">
    <block type="robot_move"></block>
    <block type="robot_rotate"></block>
    <block type="robot_set_angle"></block>
    <block type="robot_set_all_angles"></block>
  </category>

  <category name="Positions" colour="#5CA699">
    <block type="robot_record_position"></block>
    <block type="robot_move_to_recorded"></block>
  </category>

  <category name="Gripper" colour="#A65C81">
    <block type="robot_grip"></block>
    <block type="robot_release"></block>
  </category>

  <category name="Control" colour="#5CA65C">
    <block type="controls_if"></block>
    <block type="controls_repeat_ext"></block>
  </category>

  <category name="Logic" colour="#5C68A6">
    <block type="logic_compare"></block>
    <block type="logic_boolean"></block>
  </category>

  <category name="Math" colour="#A6745C">
    <block type="math_number"></block>
    <block type="math_arithmetic"></block>
  </category>

  <category name="Variables" custom="VARIABLE" colour="#5CA6A6"></category>
  <category name="Functions" custom="PROCEDURE" colour="#A65C5C"></category>
</xml>
`;
