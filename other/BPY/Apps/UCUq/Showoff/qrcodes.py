import json
import pathlib

CONFIG_FILE_NAME_ = "config.json"

def getQRCodes_():
  file = pathlib.Path(CONFIG_FILE_NAME_)

  if not file.exists() or not file.is_file():
    return []

  with open(CONFIG_FILE_NAME_, "r", encoding="utf-8") as config:
    config = json.load(config)

  if "QRCodes" in config:
    return config["QRCodes"]
  else:
    return []


def getQRCodesHTML_(qrCodesList):
  html = "<option disabled selected>Choose</option>"
  isGroup = False

  for qrCodes in qrCodesList:
    isGroup = False

    if qrCodes[0] != "":
      isGroup = True
      html += f"<optgroup label='{qrCodes[0]}'>\n"

    for qrCode in qrCodes[1]:
      html += f"<option value='{qrCode[0]}'>{qrCode[1]}</option>\n"

    if isGroup:
      html += "</optgroup>\n"

  return html


def set(dom):
  qrCodes = getQRCodes_()

  html = getQRCodesHTML_(qrCodes)

  dom.inner("QRCodesList", html)
