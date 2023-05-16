<?php
/*
Copyright (C) 2015 Claude SIMON (http://q37.info/contact/).

This file is part of xdhwebq.

xdhwebq is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

xdhwebq is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with xdhwebq. If not, see <http://www.gnu.org/licenses/>.
*/

const PATTERN = "_supplier=qrcode";

$rawUrl = $_REQUEST['url'];
$url = str_replace("&" . PATTERN, "", $rawUrl);
$detailsOpenAttribute = strpos($rawUrl, PATTERN) ? 'open="open"' : "";
$qrCodeId = "QRCode";

echo <<<EOS
<head>
  <script src="qrcode.min.js"></script>
  <script src="clipboard.min.js"></script>
  <script>
    function adjustHeight() {
      let iframe = window.frameElement;
      iframe.height = '50px';
      let body = document.body;
      iframe.height = body.scrollHeight + 'px';
      document.getElementById("$qrCodeId").scrollIntoView();
    }
  </script>
  <style>
    body div {
      font-size: 1rem;
      margin: auto;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
      width: 100%;
      background: #ffffff;
      border-radius: 8px;
      position: relative;
      width: 150px;
    }
  </style>
  <script>
  function toggle() {
    var x = document.getElementById("$qrCodeId");
    if (x.style.display === "none") {
      x.style.display = "flex";
    } else {
      x.style.display = "none";
    }
    adjustHeight();
  }  
  </script>
  <style>
  .popup {
    position: relative;
    display: inline-block;
    cursor: pointer;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
  }
  
  .popup .popuptext {
    visibility: hidden;
    width: 160px;
    background-color: #555;
    color: #fff;
    text-align: center;
    border-radius: 6px;
    padding: 8px 0;
    position: absolute;
    z-index: 1;
    left: -100;
    margin-left: -80px;
  }
  
  .popup .show {
    padding: 10px;
    visibility: visible;
    -webkit-animation: fadeIn 1s;
    animation: fadeIn 1s;
  }
  
  @-webkit-keyframes fadeIn {
    from {opacity: 0;} 
    to {opacity: 1;}
  }
  
  @keyframes fadeIn {
    from {opacity: 0;}
    to {opacity:1 ;}
  }
  </style>
  <script>
  function copy() {
    if (window.isSecureContext) {
      navigator.clipboard.writeText("$url");
      var popup = document.getElementById("copyReport");
      popup.classList.toggle("show");
      setTimeout(() => popup.classList.remove("show"), 2500);
    } else
      alert("Clipboard copy not available in this context.\\nPlease copy the URL directly from the address bar of your browser.");
  }
  </script>  
</head>

<body onload="new QRCode('$qrCodeId', {width:100, height:100, correctLevel: QRCode.CorrectLevel.L}).makeCode('$url');adjustHeight();">
  <div>
    <div style="justify-content: space-around; display: flex;">
      <span>
        <!--img title="Share" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAY1JREFUSEu11D9IllEUx/GPgwQlBLlFSyFWEkRBQkRhqyIEClkEDRUNjU21JEREERHZVC4iIjYI2VbZ4BK0JOngZn+IliCaIoqUA1d4eXjV+7zv452eeznP73vPOb9zW2zxatlifc0AdqMbn/AR/+tdtlHADZzAG3RgLy7iRxHSCKAXfbhWI9aDy7hQBWAMN/GtIPYaAf9be95IBi8whN8FwDQu4WezgAk8R4DW1k68xKlmShQiz7CM47idmrwfj/AQr8oA9mAf5tGJx7iFqHU7wklHE/AJPpSxaThkAHPox5+0/152MOs1eRdmcQz/EPunGCwrHvH1AIcwXBCcwtmqAK14j3NYQgxRfF+tChA6XXiAHficnoPI4GtZSO6gBTAseheHsZB8v7IZMBcQOvfRhhkcwcH0wG0IyQVsxyjO19z4evL+242yyAXEtJ7BvRqxkziQSrcuIxcQzhpPbloryR1MYrGKDELjNK7gHWJWQnikyiaH1rb0Ln3Br83E15vknP+yY3J7kC1YDFwFs5xCGUoFddYAAAAASUVORK5CYII="/>
        <span style="vertical-align: middle; height: 100%; display: inline-block;">:</span-->
        <!--a style="color: transparent;" target="_blank" href="$url">
          <img title="Open another session" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAVtJREFUSEvd1T1LHVEQh/GfSHwhKDEp7MQmKbQU8wFiaRNSmNgJFoJgnSY2dhaCnS8gJGVA0N4Ugk0KIVUUO0s7QcRGURnYhcty7nJy75WA0yzszplnzn9mZ7o8sXU9cXzNAL14i3hW7RQ36MN4kwTPcB3fUoB5LOAPLhMBfiAgkUD4NtpAcXYR2ynAEkbxFXf/KF8E38M5jrFZBbzBLqZw32LwVUScVynANCaw0kbwA3xpBviMoZKcCXlZ3HoNv4ozHQOkggejI4CyoKF5yNJo0V09+Fstcq5EzTJPqtr4H+QA6jIvAf14gatWbvAOwziqaYKZolm2WgHkNFdHilwHesaATxjBeo7QNT5z6MZOtchjWMZsm4CYot/xOzWuf2IDhy1CJvENH/GQArxGLJSTYgSkFk6KPYgPCEBIdFE6pTZavIvR/b6YKTmXuS024H51l/y3pZ+TdZbPI18eRxnb8aT1AAAAAElFTkSuQmCC"/>
        </a-->
        <span onclick="toggle();" style="cursor: pointer">
            <img title="Displays the QR code to scan to access the application" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAQ9JREFUSEu1lLENAjEQBOdFA1AIJFQABRBRBogKSKACRBuQUABUQEQhUAKyZKT1iUNnrP/o9V7/2Ht719Hz0/X8fxQwAbbA0EBfwA54AOu8dgQi+gJwAubA3QCmwBVYAre8NgMi+gKgm5Wh3713T+8CVsAAOJhTewBP7wI2+UgWoDVQmKevtsi1QhYKqzVFZyAV71eR1YqIvrjBOMd0ZFL0BPY5pmpFRF8Aeuk5tUivn4q5EOIFSM1lNUmSvmvxVVPcQK/vAby0eIlqsijSdNWzKNKArkWR2WJt/FYD1TQ1Wih1miL11LPCFt+DfFL31yzS+P4NiMycaosis0WtizRm0yyKNGZTo1VbFNpQK3oD3s5tGW4LqcAAAAAASUVORK5CYII="/>
        </span>
        <span class="popup" onclick="copy()">
          <img title="Copies the link to the application in the clipboard" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAONJREFUSEvt1cFJQ0EQxvFfSrCDkAZysAFz85CruYghaAsWYAHpIenAS+6xBG1A7MBbiOBBBjYQw9u3L+E9BMnAXJbh+883LDM9HUevY31/DnjCGJ8VTqO5DSbY5iZRchCAl5T7Glf4wCVmuMlBcoA5hhjgoQKwDw4Ht8nJ16GTHGCNEXIODt8Dco37NgH9NKbQXGKRmvrFONVBiEfu4hXPbQKqPs1urK04OAOUvul5RP9oRFPc1RylC0S+4w2Px+6i0sGLtR0Zy68y6nbRd0k9db86BdBAu1lJ6aI1U6mp6hzwA2dATRlJV2KvAAAAAElFTkSuQmCC"/>
          <span class="popuptext" style="width: max-content;" id="copyReport">Link to application copied</span> 
        </span>
      </span>
      <a href="https://atlastk.org" target="_blank">
        <img title="Powered by the Atlas toolkit" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAbpJREFUSEul1E2IT2EUBvDfZHyUZkOJsNAsRo2ylA0LaWQjZGUslWZlLJCPko+wYkqUsvHRbIZhpWwsfGQ7FAmRj5W1hRWdeqdub/d/7/u/825u3fc9z3POc55zBpSfrVje8HwOv/P7gUL8cdxreTuDA10IIuuP+IXTNSRHsB9jeNaF4DzOYBteZgDr8QFP67KPt20SrUvZP8KhmuwfYhdG8a1OwjaCaezBRnzPAHYmSU7hcq/+NBGEa14hJDqXASzBWyzCJvztlyCI32AtRvAnA4isL2F30r+nwXpVEHrfTbrfz6JX4zMG8aJyN4ubJS6at+VPhEz/sqBVuINl6f92LMZZXCwhuJD8XmfLPP4KTuA6JktctAZfUtavKwFPcCMDuIajiO+x0ibn5Q9hC25hogJSBF4yaMdxFZuTLSOmVZZqNU1zEB7/hK/YkYL6Am+rYB9iFezF4zStJ5saWtLk6pvn2IDhZL++wZsqiOX1DtGDlegE3kRwGwfxAIf7laWtySvwA0vTMoshCp/nE91z/7QRxGSGW+IsCLxOonlrRnMXDF5HELs9mjuVdksnWdokCge976p53pj/x8VXGXemjWsAAAAASUVORK5CYII="/>
      </a>
    </div>
    <a style="color: transparent;" target="_blank" href="$url">
      <div title="$url" style="display: none; justify-content: space-around; padding: 5px 0px 10px" id="$qrCodeId"></div>
    </a>
    </div>
</body>
EOS;
?>
