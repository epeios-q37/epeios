import json
import subprocess

import shared


_devices = None

_PARTNER_DIALOG = """\
<div style="display: flex; flex-direction: column; gap: 5px;">
  <fieldset id="PartnerDevicesList" style="display: flex; flex-direction: column;">
  </fieldset>
  <span style="display: flex; justify-content: space-around; gap: 5px;">
    <button xdh:onevent="PartnerDevicesOK">OK</button>
    <button xdh:onevent="PartnerDevicesCancel">Cancel</button>
    <button xdh:onevent="PartnerDevicesRefresh">Refresh</button>
  </span>
</div>
"""

_PARTNER_ITEM = """\
<div style="display: flex; justify-content: space-between; gap: 5px;">
<label style="display: flex; justify-content: space-between; width: 100%;">
  <span>{device}: </span>
  <input id="PartnerDevice{index}" type="checkbox" {checked}></input>
</label>
<span xdh:onevent="PartnerDeviceClose" xdh:mark="{device}" style="cursor: default;">⏏</span>
</div>
"""

_SHOW_DIALOG = """\
<fieldset style="display: flex; flex-direction: column; gap: 5px;">
  <legend>Show device</legend>
  <fieldset id="ShowDevicesList" style="display: grid;  grid-template-columns: repeat(6, 1fr); align-items: center;">
  </fieldset>
  <span style="display: flex; justify-content: space-around; gap: 5px;">
    <button xdh:onevent="ShowDevicesOK">OK</button>
    <button xdh:onevent="ShowDevicesCancel">Cancel</button>
    <button xdh:onevent="ShowDevicesRefresh">Refresh</button>
  </span>
</fieldset>
"""

_SHOW_HEADER = """\
  <span>Sites: </span>
  {}
  <span>⌫</span>
  <span></span>
"""

_SHOW_HEADER_ITEM = '<span style="justify-self: center;">{}</span>'

_SHOW_BODY_ITEM = """\
    <span>{device}: </span>
    <span style="display: none;" xdh:radio="ShowDevice{index}" id="ShowDevice{index}"></span>
    {sites}
    <span onclick="document.querySelectorAll('input[type=&quot;radio&quot;][name=&quot;ShowDevice{index}&quot;]').forEach(radio =&gt; {{radio.checked = false;}});">⌫</span>
    <span xdh:onevent="PartnerDeviceClose" xdh:mark="{device}" style="cursor: default;">⏏</span>
"""


_SHOW_BODY_SUB_ITEM = '<input name="ShowDevice{index}" value="{site}" type="radio" {checked}></input>'



def getDevices():
  global _devices

  _devices = json.loads(subprocess.run(("ucuqm", "--fetch", "--json"), capture_output=True, check=True).stdout)["Ids"]

  return _devices


def _closeDevices():
  subprocess.run(("ucuqm", "--close"), check=False)


def _closeDevice(device):
  subprocess.run(("ucuqm", "--close", device), check=False)


def _getPartnerDevicesDialog():
  return "document.getElementById('PartnerDevices')"


def _fillPartnerDevices(dom):
  devices = dom.getValue("PartnerDevice").split()

  dom.inner("PartnerDevicesList", "\n".join(_PARTNER_ITEM.format(device=device, index=index, checked="checked" if device in devices else "") for index, device in enumerate(getDevices())))


def atkPartnerDevicesOK(dom):
  dom.executeVoid(f"{_getPartnerDevicesDialog()}.close()")

  ids = [f"PartnerDevice{index}" for index in range(len(_devices))]

  dom.setValue("PartnerDevice", " ".join([_devices[int(k[13:])] for k, v in dom.getValues(ids).items() if v == "true"]))


def atkPartnerDevicesCancel(dom):
  dom.executeVoid(f"{_getPartnerDevicesDialog()}.close()")


def atkPartnerDevicesRefresh(dom):
  dom.setValue("PartnerDevicesList", "")
  _fillPartnerDevices(dom)


def atkPartnerDevicesRAZ(dom):
  _closeDevices()
  dom.setValue("PartnerDevicesList", "")


def atkPartnerDeviceClose(dom, id):
  _closeDevice(dom.getMark(id))
  dom.setValue("PartnerDevicesList", "")
  _fillPartnerDevices(dom)

def atkPartnerSelect(dom):
  dom.inner("PartnerDevices", _PARTNER_DIALOG)

  _fillPartnerDevices(dom)  

  dom.executeVoid(f"{_getPartnerDevicesDialog()}.showModal();")


def _getShowDevicesDialog():
  return "document.getElementById('ShowDevices')"


def _fillShowDevices(dom):
  devices = dom.getValues(shared.SHOW_SITES_INPUT)

  header = _SHOW_HEADER.format("\n".join(_SHOW_HEADER_ITEM.format(site.lower()) for site in shared.SHOW_SITES))

  body = "\n".join(_SHOW_BODY_ITEM.format(device=device, index=index, sites = "\n".join(_SHOW_BODY_SUB_ITEM.format(index=index, site=site, checked="checked" if device in devices[f"Show{site}Device"].split() else "") for site in shared.SHOW_SITES)) for index, device in enumerate(getDevices()))

  dom.setValue("ShowDevicesList", f'{header}\n{body}')


def atkShowDevicesOK(dom):
  dom.executeVoid(f"{_getShowDevicesDialog()}.close()")

  sites = { int(key[10:]): value for key, value in dom.getValues([f"ShowDevice{index}" for index in range(len(_devices))]).items() }

  dom.setValues({
    f"Show{site}Device": " ".join([_devices[key] for key, valeur in sites.items() if valeur == site]) for site in shared.SHOW_SITES})


def atkShowDevicesCancel(dom):
  dom.executeVoid(f"{_getShowDevicesDialog()}.close()")


def atkShowDevicesRefresh(dom):
  dom.setValue("ShowDevicesList", "")
  _fillShowDevices(dom)


def atkShowDevicesRAZ(dom):
  _closeDevices()
  dom.setValue("ShowDevicesList", "")


def atkShowSelect(dom):
  dom.inner("ShowDevices", _SHOW_DIALOG)

  _fillShowDevices(dom)

  dom.executeVoid(f"{_getShowDevicesDialog()}.showModal();")
  

__all__ = [nom for nom in dir() if nom.startswith("atk")]