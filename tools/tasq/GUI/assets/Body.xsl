<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:xdh="http://q37.info/ns/xdh"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xpp="http://epeios.q37.info/ns/xpp">
  <xpp:expand href="item.sub.xsl" />
  <xsl:output method="html" indent="yes" />
  <xsl:template name="TaskEventLoop">
    <xsl:param name="i">0</xsl:param>
    <xsl:param name="step">1</xsl:param>
    <xsl:param name="last" />
    <xsl:param
      name="selected" />
    <option>
      <xsl:attribute name="value">
        <xsl:value-of select="$i" />
      </xsl:attribute>
      <xsl:if test="$i = $selected">
        <xsl:attribute name="selected">true</xsl:attribute>
      </xsl:if>
      <xsl:value-of select="format-number($i, '00')" />
    </option>
    <xsl:if test="$i &lt; $last">
      <xsl:call-template name="TaskEventLoop">
        <xsl:with-param name="i" select="$i + $step" />
        <xsl:with-param name="step" select="$step" />
        <xsl:with-param name="last" select="$last" />
        <xsl:with-param name="selected" select="$selected" />
      </xsl:call-template>
    </xsl:if>
  </xsl:template>
  <xsl:template match="/TASq">
    <div style="display: flex; flex-direction: column; width: 700px;">
      <fieldset>
        <fieldset id="Tree" style="height: 200px; overflow: auto;"></fieldset>
        <div class="buttons">
          <button id="New" xdh:onevent="New">New</button>
          <button id="Edit" xdh:onevent="Edit">Edit</button>
          <button id="Delete" xdh:onevent="Delete">Delete</button>
          <button id="Move" xdh:onevent="Move">Move</button>
        </div>
      </fieldset>
      <fieldset>
        <div>
          <fieldset id="TitleView"></fieldset>
          <input style="width: 100%;" class="hide" id="TitleEdition" />
          <xsl:apply-templates select="Corpus/Task" />
          <fieldset>
            <div style="height: 100px; overflaow: auto;" id="DescriptionView"></div>
            <textarea class="hide" id="DescriptionEdition"></textarea>
          </fieldset>
          <div class="buttons">
            <button id="Submit" xdh:onevent="Submit">Submit</button>
            <button id="Cancel" xdh:onevent="Cancel">Cancel</button>
          </div>
        </div>
      </fieldset>
    </div>
  </xsl:template>
  <xsl:template match="Corpus/Task">
    <xsl:apply-templates select="Status" />
  </xsl:template>
  <xsl:template match="Corpus/Task/Status">
    <div id="TaskStatusEdition" class="hide">
      <div style="display: flex; flex-direction: row;">
        <xsl:apply-templates select="Types" />
        <div id="TaskTimelyFeatures" class="hide">
          <label>
            <span>Before:</span>
            <input id="TaskTimelyDateEarliest" placeholder="Earliest" title="Earliest" class="date"></input>
          </label>
          <label>
            <span>After:</span>
            <input id="TaskTimelyDateLatest" placeholder="Latest" title="Latest" class="date"></input>
          </label>
        </div>
        <div id="TaskEventFeatures" class="hide">
          <div style="display: flex; flex-direction: row;">
            <input id="TaskEventDate" class="date"></input>
            <div id="TaskEventTime">
              <div style="display: flex; flex-direction: row;">
                <select id="TaskEventTimeHour">
                  <xsl:call-template name="TaskEventLoop">
                    <xsl:with-param name="step">1</xsl:with-param>
                    <xsl:with-param name="last">23</xsl:with-param>
                    <xsl:with-param name="selected">12</xsl:with-param>
                  </xsl:call-template>
                </select>
                <span>:</span>
                <select id="TaskEventTimeMinute">
                  <xsl:call-template name="TaskEventLoop">
                    <xsl:with-param name="step">5</xsl:with-param>
                    <xsl:with-param name="last">55</xsl:with-param>
                  </xsl:call-template>
                </select>
              </div>
            </div>
          </div>
        </div>
        <div id="TaskRecurrentFeatures" class="hide">
          <input id="TaskRecurrentSpan" min="1" type="number" />
          <xsl:apply-templates select="Unites" />
        </div>
      </div>
    </div>
  </xsl:template>
  <xsl:template match="Task/Status/Types">
    <select id="TaskStatusType" xdh:onevent="SelectTaskType">
      <xsl:apply-templates select="Type" />
    </select>
  </xsl:template>
  <xsl:template match="Task/Status/Types/Type">
    <option value="{@id}">
      <xsl:value-of select="@Label" />
    </option>
  </xsl:template>
  <xsl:template match="Task/Status/Unites">
    <select id="TaskRecurrentUnit">
      <xsl:apply-templates select="Unit" />
    </select>
  </xsl:template>
  <xsl:template match="Task/Status/Unites/Unit">
    <option value="{@id}">
      <xsl:value-of select="@Label" />
    </option>
  </xsl:template>
</xsl:stylesheet>