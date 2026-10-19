import json
import subprocess

import show

_devices = None

_PARTNER_DIALOG = """\
<div style="display: flex; flex-direction: column; column-gap: 5px;">
  <span style="display: flex; justify-content: space-between; gap: 5px;">
    <span style="display: flex; justify-content: space-between; width: 100%;">
      <span>Device</span>
      <input type="checkbox" onchange="document.querySelectorAll('input[type=&quot;checkbox&quot;][class=&quot;PartnerDevices&quot;]').forEach(checkbox =&gt; {{checkbox.checked=this.checked;}});"></input>
    </span>
    <span xdh:onevent="PartnerDevicesCloseAll" style="cursor: default;">⏏</span>
  </span>
  <hr style="width: 100%;">
  <span id="PartnerDevicesList" style="display: flex; flex-direction: column;"></span>
  <span style="display: flex; justify-content: space-around; column-gap: 5px; margin-top: 20px;">
    <button xdh:onevent="PartnerDevicesOK">OK</button>
    <button xdh:onevent="PartnerDevicesCancel">Cancel</button>
    <button xdh:onevent="PartnerDevicesRefresh">Refresh</button>
  </span>
</div>
"""

_PARTNER_ITEM = """\
<div style="display: flex; justify-content: space-between; gap: 5px;">
  <label style="display: flex; justify-content: space-between; width: 100%;">
    <span>{device}</span>
    <input id="PartnerDevice{index}" type="checkbox" class="PartnerDevices" {checked}></input>
  </label>
  <span xdh:onevent="PartnerDevicesClose" xdh:mark="{device}" style="cursor: default;">⏏</span>
</div>
"""

_SHOW_DIALOG = """\
<span style="display: grid;  grid-template-columns: repeat(6, auto); align-items: center; column-gap: 10px;">
  <span>Device </span>
  {}
  <span style="justify-self: center; cursor: default;"onclick="document.querySelectorAll('input[type=&quot;radio&quot;]').forEach(radio =&gt; {{radio.checked = false;}});">⌫</span>
  <span style="justify-self: center;cursor: default; " xdh:onevent="ShowDevicesCloseAll"">⏏</span>
  <hr id="ShowDevicesList" style="grid-column: 1/7; width : 100%;">
</span>
<span style="display: flex; justify-content: space-around; column-gap: 5px; margin-top: 20px;">
  <button xdh:onevent="ShowDevicesOK">OK</button>
  <button xdh:onevent="ShowDevicesCancel">Cancel</button>
  <button xdh:onevent="ShowDevicesRefresh">Refresh</button>
</span>
"""

_SHOW_HEADER_ITEM = '<span style="justify-self: center;">{}</span>'

_SHOW_LIST_ITEM = """\
<span xdh:radio="ShowDevice{index}" id="ShowDevice{index}">{device}</span>
{sites}
<span style="justify-self: center; cursor: default;" onclick="document.querySelectorAll('input[type=&quot;radio&quot;][name=&quot;ShowDevice{index}&quot;]').forEach(radio =&gt; {{radio.checked = false;}});">⌫</span>
<span style="justify-self: center; cursor: default;" xdh:onevent="ShowDevicesClose" xdh:mark="{device}">⏏</span>
"""

_SHOW_LIST_SUB_ITEM = '<input name="ShowDevice{index}" value="{site}" type="radio" {checked}></input>'


def getDevices():
  global _devices

  _devices = json.loads(subprocess.run(("ucuqm", "--fetch", "--json"), capture_output=True, check=True).stdout)["Ids"]

  return _devices


def _closeAllDevices():
  subprocess.run(("ucuqm", "--close"), check=False)


def _closeDevice(device):
  subprocess.run(("ucuqm", "--close", device), check=False)


def _getPartnerDevicesDialog():
  return "document.getElementById('PartnerDevices')"


def _fillPartnerDevices(dom):
  dom.setValue("PartnerDevicesList", "")
  devices = dom.getValue("PartnerDevice").split()
  dom.inner("PartnerDevicesList", "\n".join(_PARTNER_ITEM.format(device=device, index=index, checked="checked" if device in devices else "") for index, device in enumerate(getDevices())))


def atkPartnerDevicesOK(dom):
  dom.executeVoid(f"{_getPartnerDevicesDialog()}.close()")

  ids = [f"PartnerDevice{index}" for index in range(len(_devices))]

  dom.setValue("PartnerDevice", " ".join([_devices[int(k[13:])] for k, v in dom.getValues(ids).items() if v == "true"]))


def atkPartnerDevicesCancel(dom):
  dom.executeVoid(f"{_getPartnerDevicesDialog()}.close()")


def atkPartnerDevicesRefresh(dom):
  _fillPartnerDevices(dom)


def atkPartnerDevicesCloseAll(dom):
  _closeAllDevices()
  _fillPartnerDevices(dom)


def atkPartnerDevicesClose(dom, id):
  _closeDevice(dom.getMark(id))
  _fillPartnerDevices(dom)


def atkPartnerSelect(dom):
  dom.inner("PartnerDevices", _PARTNER_DIALOG)

  _fillPartnerDevices(dom)  

  dom.executeVoid(f"{_getPartnerDevicesDialog()}.showModal();")


def _getShowDevicesDialog():
  return "document.getElementById('ShowDevices')"


def _fillShowDevices(dom):
  dom.executeVoid("removeFollowingSiblings('ShowDevicesList')")

  devices = dom.getValues(show.SHOW_SITES_INPUT)

  list = "\n".join(_SHOW_LIST_ITEM.format(device=device, index=index, sites = "\n".join(_SHOW_LIST_SUB_ITEM.format(index=index, site=site, checked="checked" if device in devices[f"Show{site}Device"].split() else "") for site in show.SHOW_SITES)) for index, device in enumerate(getDevices()))

  dom.after("ShowDevicesList", list)


def atkShowDevicesOK(dom):
  dom.executeVoid(f"{_getShowDevicesDialog()}.close()")

  sites = { int(key[10:]): value for key, value in dom.getValues([f"ShowDevice{index}" for index in range(len(_devices))]).items() }

  dom.setValues({
    f"Show{site}Device": " ".join([_devices[key] for key, valeur in sites.items() if valeur == site]) for site in show.SHOW_SITES})


def atkShowDevicesCancel(dom):
  dom.executeVoid(f"{_getShowDevicesDialog()}.close()")


def atkShowDevicesRefresh(dom):
  _fillShowDevices(dom)


def atkShowDevicesCloseAll(dom):
  _closeAllDevices()
  _fillShowDevices(dom)


def atkShowDevicesClose(dom, id):
  _closeDevice(dom.getMark(id))
  _fillShowDevices(dom)


def atkShowSelect(dom):
  dom.inner("ShowDevices", _SHOW_DIALOG.format("\n".join(_SHOW_HEADER_ITEM.format(site.lower()) for site in show.SHOW_SITES)))

  _fillShowDevices(dom)

  dom.executeVoid(f"{_getShowDevicesDialog()}.showModal();")
  

__all__ = [nom for nom in dir() if nom.startswith("atk")]