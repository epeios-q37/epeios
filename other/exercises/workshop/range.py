#!/usr/bin/python3
# coding: utf8

# Si installé avec 'pip install term2web',
# les deux lignes suivanes peuvent être retirée.
import sys, os
sys.path.append("./Atlas.zip")

import os
import atlastk as Atlas

head = """
<title>" + os.path.splitext(__file__)[0] + " - Atlas toolkit</title>
<link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgBAMAAACBVGfHAAAAMFBMVEUEAvyEhsxERuS8urQsKuycnsRkYtzc2qwUFvRUVtysrrx0ctTs6qTMyrSUksQ0NuyciPBdAAABHklEQVR42mNgwAa8zlxjDd2A4POfOXPmzZkFCAH2M8fNzyALzDlzg2ENssCbMwkMOsgCa858YOjBKxBzRoHhD7LAHiBH5swCT9HQ6A9ggZ4zp7YCrV0DdM6pBpAAG5Blc2aBDZA68wCsZPuZU0BDH07xvHOmAGKKvgMP2NA/Zw7ADIYJXGDgLQeBBSCBFu0aoAPYQUadMQAJAE29zwAVWMCWpgB08ZnDQGsbGhpsgCqBQHNfzRkDEIPlzFmo0T5nzoMovjPHoAK8Zw5BnA5yDosDSAVYQOYMKIDZzkoDzagAsjhqzjRAfXTmzAQgi/vMQZA6pjtAvhEk0E+ATWRRm6YBZuScCUCNN5szH1D4TGdOoSrggtiNAH3vBBjwAQCglIrSZkf1MQAAAABJRU5ErkJggg==" />
"""

def prettify(body):
    return """
<div style="display: table; margin: 50px auto auto auto;">
 <fieldset>
""" + body + """
 </fieldset>
</div>
"""

# End of header.

body = """
<label for="volume">Volume</label>
<input type="range" id="volume" min="0" max="10" data-xdh-onevent="Slide">
<meter id="fuel"
  min="0" max="10"
  low="5" high="8" optimum="4"
  value="5">
</meter>
"""

def ac_connect(dom):
	dom.set_layout("", prettify(body))
	dom.focus("volume")

def ac_slide(dom):
	dom.set_attribute("fuel", "value", (dom.getContent("volume")))

callbacks = {
	"": ac_connect,
	"Slide": ac_slide
}

Atlas.launch(callbacks, None, head)
