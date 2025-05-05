<?php

$lang = $_REQUEST["lang"] ?? "";
$demo = $_REQUEST["demo"] ?? "";
$code = $_REQUEST["code"] ?? "";
$cxml = $_REQUEST["xml"] ?? ""; // Compressed with 'Q_COMPRESS'!!!
$use_ucuq_demo_devices = isset($_REQUEST["useUCUqDemoDevices"]) ? "true" : "false";

$use_ucuq_demo_devices_field = $use_ucuq_demo_devices === "true"? "<input type='hidden' name='useUCUqDemoDevices' value='' />\n" : '';


echo <<<BODY
<!DOCTYPE html>
<html>

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="google" value="notranslate">
  <title>UCUq with Blockly</title>
  <link rel="stylesheet" href="style.css">
  <script src="https://unpkg.com/blockly/blockly_compressed.js"></script>
  <script src="https://unpkg.com/blockly/blocks_compressed.js"></script>
  <script src="https://unpkg.com/blockly/javascript_compressed.js"></script>
  <script src="https://unpkg.com/blockly/python_compressed.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/pako/2.1.0/pako.min.js"></script>
  <!--script src="https://unpkg.com/blockly/php_compressed.js"></script-->
  <!--script src="https://unpkg.com/blockly/lua_compressed.js"></script-->
  <!--script src="https://unpkg.com/blockly/dart_compressed.js"></script-->
  <script type="text/javascript">
    const LANG = `$lang`;
    const DEMO = `$demo`;
    const CODE = `$code`;
    const CXML = `$cxml`;
    const USE_UCUQ_DEMO_DEVICES = $use_ucuq_demo_devices;
  </script>
  <script src="tools.js"></script>
  <script src="code.js"></script>
  <script src="ucuq.js"></script>
  <script type="text/javascript">
    function launchCode(code) {
      document.getElementById("code").value = pack(code);
      document.getElementById('brython').submit();
    }
    ucuq = require("ucuq");
  </script>
</head>
<body onload="init()">
  <table width="100%" height="100%">
    <tr>
      <td>
        <h1>
          <span><em>UCUq</em></span>
          <span>&rlm; &gt;</span>
          <span><em>Blockly</em></span>
          <span>&rlm; &gt;</span>
          <span id="title">...</span>
        </h1>
      </td>
      <td class="farSide">
        <select id="languageMenu"></select>
        <a class="privacyLink" href="https://policies.google.com/privacy">Privacy</a>
      </td>
    </tr>
    <tr>
      <td colspan=2>
        <table width="100%">
          <tr id="tabRow" height="1em">
            <td id="tab_blocks" class="tabon">...</td>
            <td class="hide tabmin tab_collapse">&nbsp;</td>
            <td id="tab_javascript" class="hide taboff tab_collapse">JavaScript</td>
            <td class="tabmin tab_collapse">&nbsp;</td>
            <td id="tab_python" class="taboff tab_collapse">Python</td>
            <td class="hide tabmin tab_collapse">&nbsp;</td>
            <td id="tab_php" class="hide taboff tab_collapse">PHP</td>
            <td class="hide tabmin tab_collapse">&nbsp;</td>
            <td id="tab_lua" class="hide taboff tab_collapse">Lua</td>
            <td class="hide tabmin tab_collapse">&nbsp;</td>
            <td id="tab_dart" class="hide taboff tab_collapse">Dart</td>
            <td class="tabmin tab_collapse">&nbsp;</td>
            <td id="tab_xml" class="taboff tab_collapse">XML</td>
            <td class="tabmin tab_collapse">&nbsp;</td>
            <td id="tab_json" class="taboff tab_collapse">JSON</td>
            <td class="tabmin">&nbsp;</td>
            <td id="tab_code" class="taboff">
              <select id="code_menu"></select>
            </td>
            <td class="tabmax">
              <button id="trashButton" class="notext" title="...">
                <img src='media/1x1.gif' class="trash icon21">
              </button>
              <button id="linkButton" class="notext" title="...">
                <img src='media/1x1.gif' class="link icon21">
              </button>
              <button id="runButton" class="notext primary" title="...">
                <img src='media/1x1.gif' class="run icon21">
              </button>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td height="99%" colspan=2 id="content_area">
      </td>
    </tr>
  </table>
  <div id="content_blocks" class="content"></div>
  <!--pre id="content_javascript" class="content prettyprint lang-js"></pre-->
  <pre id="content_python" class="content prettyprint lang-py"></pre>
  <!--pre id="content_php" class="content prettyprint lang-php"></pre-->
  <!--pre id="content_lua" class="content prettyprint lang-lua"></pre-->
  <!--pre id="content_dart" class="content prettyprint lang-dart"></pre-->
  <textarea id="content_xml" class="content" wrap="off"></textarea>
  <textarea id="content_json" class="content" wrap="off"></textarea>

  <xml xmlns="https://developers.google.com/blockly/xml" id="toolbox" style="display: none">
    <category name="%{BKY_CATLOGIC}" colour="%{BKY_LOGIC_HUE}">
      <block type="controls_if"></block>
      <block type="logic_compare"></block>
      <block type="logic_operation"></block>
      <block type="logic_negate"></block>
      <block type="logic_boolean"></block>
      <block type="logic_null"></block>
      <block type="logic_ternary"></block>
    </category>
    <category name="%{BKY_CATLOOPS}" colour="%{BKY_LOOPS_HUE}">
      <block type="controls_repeat_ext">
        <value name="TIMES">
          <shadow type="math_number">
            <field name="NUM">10</field>
          </shadow>
        </value>
      </block>
      <block type="controls_whileUntil"></block>
      <block type="controls_for">
        <value name="FROM">
          <shadow type="math_number">
            <field name="NUM">1</field>
          </shadow>
        </value>
        <value name="TO">
          <shadow type="math_number">
            <field name="NUM">10</field>
          </shadow>
        </value>
        <value name="BY">
          <shadow type="math_number">
            <field name="NUM">1</field>
          </shadow>
        </value>
      </block>
      <block type="controls_forEach"></block>
      <block type="controls_flow_statements"></block>
    </category>
    <category name="%{BKY_CATMATH}" colour="%{BKY_MATH_HUE}">
      <block type="math_number">
        <field name="NUM">123</field>
      </block>
      <block type="math_arithmetic">
        <value name="A">
          <shadow type="math_number">
            <field name="NUM">1</field>
          </shadow>
        </value>
        <value name="B">
          <shadow type="math_number">
            <field name="NUM">1</field>
          </shadow>
        </value>
      </block>
      <block type="math_single">
        <value name="NUM">
          <shadow type="math_number">
            <field name="NUM">9</field>
          </shadow>
        </value>
      </block>
      <block type="math_trig">
        <value name="NUM">
          <shadow type="math_number">
            <field name="NUM">45</field>
          </shadow>
        </value>
      </block>
      <block type="math_constant"></block>
      <block type="math_number_property">
        <value name="NUMBER_TO_CHECK">
          <shadow type="math_number">
            <field name="NUM">0</field>
          </shadow>
        </value>
      </block>
      <block type="math_round">
        <value name="NUM">
          <shadow type="math_number">
            <field name="NUM">3.1</field>
          </shadow>
        </value>
      </block>
      <block type="math_on_list"></block>
      <block type="math_modulo">
        <value name="DIVIDEND">
          <shadow type="math_number">
            <field name="NUM">64</field>
          </shadow>
        </value>
        <value name="DIVISOR">
          <shadow type="math_number">
            <field name="NUM">10</field>
          </shadow>
        </value>
      </block>
      <block type="math_constrain">
        <value name="VALUE">
          <shadow type="math_number">
            <field name="NUM">50</field>
          </shadow>
        </value>
        <value name="LOW">
          <shadow type="math_number">
            <field name="NUM">1</field>
          </shadow>
        </value>
        <value name="HIGH">
          <shadow type="math_number">
            <field name="NUM">100</field>
          </shadow>
        </value>
      </block>
      <block type="math_random_int">
        <value name="FROM">
          <shadow type="math_number">
            <field name="NUM">1</field>
          </shadow>
        </value>
        <value name="TO">
          <shadow type="math_number">
            <field name="NUM">100</field>
          </shadow>
        </value>
      </block>
      <block type="math_random_float"></block>
      <block type="math_atan2">
        <value name="X">
          <shadow type="math_number">
            <field name="NUM">1</field>
          </shadow>
        </value>
        <value name="Y">
          <shadow type="math_number">
            <field name="NUM">1</field>
          </shadow>
        </value>
      </block>
    </category>
    <category name="%{BKY_CATTEXT}" colour="%{BKY_TEXTS_HUE}">
      <block type="text"></block>
      <block type="text_join"></block>
      <block type="text_append">
        <value name="TEXT">
          <shadow type="text"></shadow>
        </value>
      </block>
      <block type="text_length">
        <value name="VALUE">
          <shadow type="text">
            <field name="TEXT">abc</field>
          </shadow>
        </value>
      </block>
      <block type="text_isEmpty">
        <value name="VALUE">
          <shadow type="text">
            <field name="TEXT"></field>
          </shadow>
        </value>
      </block>
      <block type="text_indexOf">
        <value name="VALUE">
          <block type="variables_get">
            <field name="VAR">{textVariable}</field>
          </block>
        </value>
        <value name="FIND">
          <shadow type="text">
            <field name="TEXT">abc</field>
          </shadow>
        </value>
      </block>
      <block type="text_charAt">
        <value name="VALUE">
          <block type="variables_get">
            <field name="VAR">{textVariable}</field>
          </block>
        </value>
      </block>
      <block type="text_getSubstring">
        <value name="STRING">
          <block type="variables_get">
            <field name="VAR">{textVariable}</field>
          </block>
        </value>
      </block>
      <block type="text_changeCase">
        <value name="TEXT">
          <shadow type="text">
            <field name="TEXT">abc</field>
          </shadow>
        </value>
      </block>
      <block type="text_trim">
        <value name="TEXT">
          <shadow type="text">
            <field name="TEXT">abc</field>
          </shadow>
        </value>
      </block>
      <block type="text_print">
        <value name="TEXT">
          <shadow type="text">
            <field name="TEXT">abc</field>
          </shadow>
        </value>
      </block>
      <block type="text_prompt_ext">
        <value name="TEXT">
          <shadow type="text">
            <field name="TEXT">abc</field>
          </shadow>
        </value>
      </block>
    </category>
    <category name="%{BKY_CATLISTS}" colour="%{BKY_LISTS_HUE}">
      <block type="lists_create_with">
        <mutation items="0"></mutation>
      </block>
      <block type="lists_create_with"></block>
      <block type="lists_repeat">
        <value name="NUM">
          <shadow type="math_number">
            <field name="NUM">5</field>
          </shadow>
        </value>
      </block>
      <block type="lists_length"></block>
      <block type="lists_isEmpty"></block>
      <block type="lists_indexOf">
        <value name="VALUE">
          <block type="variables_get">
            <field name="VAR">{listVariable}</field>
          </block>
        </value>
      </block>
      <block type="lists_getIndex">
        <value name="VALUE">
          <block type="variables_get">
            <field name="VAR">{listVariable}</field>
          </block>
        </value>
      </block>
      <block type="lists_setIndex">
        <value name="LIST">
          <block type="variables_get">
            <field name="VAR">{listVariable}</field>
          </block>
        </value>
      </block>
      <block type="lists_getSublist">
        <value name="LIST">
          <block type="variables_get">
            <field name="VAR">{listVariable}</field>
          </block>
        </value>
      </block>
      <block type="lists_split">
        <value name="DELIM">
          <shadow type="text">
            <field name="TEXT">,</field>
          </shadow>
        </value>
      </block>
      <block type="lists_sort"></block>
    </category>
    <category name="UCUq" colour="#5C81A6">
      <block type="ucuq_connect">
        <value name="ID">
          <shadow type="ucuq_connect_id"></shadow>
        </value>
        <value name="TOKEN">
          <shadow type="ucuq_connect_token"></shadow>
        </value>
      </block>
      <block type="ucuq_sleep">
        <value name="SECONDS">
          <shadow type="ucuq_sleep_seconds"></shadow>
        </value>
    </category>
    <category name="GPIO" colour="#5C81A6">
      <block type="gpio_init">
        <value name="PIN">
          <shadow type="gpio_init_pin"></shadow>
        </value>
      </block>
      <block type="gpio_high">
        <value name="STATE">
          <shadow type="gpio_high_state"></shadow>
        </value>
      </block>
      <block type="gpio_low"></block>
    </category>
    <category name="WS2812 (RGBs)" colour="#5C81A6">
      <block type="ws2812_init">
        <value name="PIN">
          <shadow type="ws2812_init_pin"></shadow>
        </value>
        <value name="COUNT">
          <shadow type="ws2812_init_count"></shadow>
        </value>
      </block>
      <block type="ws2812_setValue">
        <value name="INDEX">
          <shadow type="ws2812_setValue_index"></shadow>
        </value>
        <value name="R">
          <shadow type="ws2812_setValue_r"></shadow>
        </value>
        <value name="G">
          <shadow type="ws2812_setValue_g"></shadow>
        </value>
        <value name="B">
          <shadow type="ws2812_setValue_b"></shadow>
        </value>
      </block>
      <block type="ws2812_fill">
        <value name="R">
          <shadow type="ws2812_fill_r"></shadow>
        </value>
        <value name="G">
          <shadow type="ws2812_fill_g"></shadow>
        </value>
        <value name="B">
          <shadow type="ws2812_fill_b"></shadow>
        </value>
      </block>
      <block type="ws2812_write"></block>
    </category>
    <category name="HD44780 (LCD)" colour="#5C81A6">
      <block type="hd44780_init">
        <value name="SOFT">
          <shadow type="hd44780_init_soft"></shadow>
        </value>
        <value name="SDA">
          <shadow type="hd44780_init_sda"></shadow>
        </value>
        <value name="SCL">
          <shadow type="hd44780_init_scl"></shadow>
        </value>
        <value name="COLS">
          <shadow type="hd44780_init_cols"></shadow>
        </value>
        <value name="ROWS">
          <shadow type="hd44780_init_rows"></shadow>
        </value>
      </block>
      <block type="hd44780_moveTo">
        <value name="X">
          <shadow type="hd44780_moveTo_x"></shadow>
        </value>
        <value name="Y">
          <shadow type="hd44780_moveTo_y"></shadow>
        </value>
      </block>
      <block type="hd44780_putString">
        <value name="STRING">
          <shadow type="hd44780_putString_string"></shadow>
        </value>
      </block>
      <block type="hd44780_clear"></block>
    </category>
    <sep></sep>
    <category name="%{BKY_CATVARIABLES}" colour="%{BKY_VARIABLES_HUE}" custom="VARIABLE"></category>
    <category name="%{BKY_CATFUNCTIONS}" colour="%{BKY_PROCEDURES_HUE}" custom="PROCEDURE"></category>
  </xml>
  <form id="brython" action="https://faas.q37.info/brython/index.php" method="POST" target="brython_result">
    <input type="hidden" name="go" value="collapse">
    <input type="hidden" id="code" name="code">
    $use_ucuq_demo_devices_field
  </form>
  <iframe name="brython_result"></iframe>
</body>

</html>
BODY
?>