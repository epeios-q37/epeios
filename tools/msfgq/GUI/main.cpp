/*
  Copyright (C) 2022 Claude SIMON (http://zeusw.org/epeios/contact.html).

  This file is part of 'MSFGq' software.

  'MSFGq' is free software: you can redistribute it and/or modify it
  under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  'MSFGq' is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with 'MSFGq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "main.h"

#include "midiq.h"
#include "registry.h"

#include "mscabc.h"
#include "mscmdd.h"

#include "mthrtn.h"

#include "cdgb64.h"
#include "rnd.h"

using namespace main;

rActionHelper main::ActionHelper;

rCore main::Core;

mscmdd::rRFlow main::MidiRFlow;

namespace {
  qENUM( Id_ ) {
    iWidthRangeInput,
    iWidthNumberInput,
    iMidiIn,
    iGrabMidiIn,
    iAccidentalAmount,
    iAccidental,
    iNumerator,
    iDenominator,
    iOctave,
    iFirst,
    iPrevious,
    iNext,
    iLast,
    iSuppr,
    iClear,
    iScripts,
    iEmbedded,
    iOutput,
    i_amount,
    i_Undefined
  };

#define C_( name )\
  case i##name:\
  return #name;\
  break

  const char *GetLabel_( eId_ Id )
  {
    switch ( Id ) {
    C_( WidthRangeInput );
    C_( WidthNumberInput );
    C_( MidiIn );
    C_( GrabMidiIn );
    C_( AccidentalAmount );
    C_( Accidental );
    C_( Numerator );
    C_( Denominator );
    C_( Octave );
    C_( First );
    C_( Previous );
    C_( Next );
    C_( Last );
    C_( Suppr );
    C_( Clear );
    C_( Scripts );
    C_( Embedded );
    C_( Output );
/*
    C_(  );
*/
    default:
      qRGnr();
      break;

    }

    return NULL;  // To avoid a warning.
  }

#undef C_

  namespace _ {
    class gl {
    public:
      static const char *GetLabel(eId_ Id)
      {
        return ::GetLabel_(Id);
      }
    };
  }

  typedef sclx::sIds<eId_, i_amount, _::gl> sIds_;
  typedef sclx::rValues<eId_, i_amount, _::gl> rValues_;
  typedef sclx::rTValues<eId_, i_amount, _::gl> rTValues_;

  sIds_
    Navigation_(iFirst, iPrevious, iNext, iLast),
    Removing_(iSuppr, iClear),
    All_(Navigation_, Removing_, iGrabMidiIn, iMidiIn);
}

#define XMEL() melody::rXMelody &XMelody = melody::Get(Guard)
#define CXMEL() const XMEL()

#define L_(name)  GetLabel_(name)

namespace {
  namespace _ {
    mtx::rMutex Mutex;
    str::wString DeviceId;
    const sSession *Owner = NULL;
  }

  void InitializeMidiInOwning_(void)
  {
    _::Mutex = mtx::Create();
    _::DeviceId.Init();
    _::Owner = NULL;
  }

  bso::sBool IsMidiInOwner_(const sSession &Session )
  {
    bso::sBool IsOwner = false;
  qRH;
    mtx::rHandle Handler;
  qRB;
    Handler.InitAndLock(_::Mutex);

    IsOwner = _::Owner == &Session;
  qRR;
  qRT;
  qRE;
    return IsOwner;
  }

  namespace _ {
    void LaunchMidiIn(sSession &Session)
    {
      midiq::sShared Shared;

      _::DeviceId.Init();
      Session.GetValue(L_( iMidiIn ), _::DeviceId);

      Shared.RFlow = &main::MidiRFlow;
      Shared.MIDIDeviceIn = &_::DeviceId;

      mtk::Launch(midiq::_HandleInput, &Shared);
    }
  }

  void GrabMidiIn_(sSession &Session )
  {
  qRH;
    mtx::rHandle Handler;
  qRB;
    Handler.InitAndLock(_::Mutex);

    if ( _::DeviceId.Amount() == 0 )
      _::LaunchMidiIn(Session);

    _::Owner = &Session;
  qRR;
  qRT;
  qRE;
  }
}

namespace {
  namespace {
    bso::sBool Fill_(
      const str::dString  &Id,
      const str::dStrings &Ids,
      const str::dStrings &Names,
      txf::rWFlow &XHTML)
    {
      sdr::sRow Row = Ids.First();
      bso::sBool Available = false;

      if ( Ids.Amount() != Names.Amount() )
        qRGnr();

      while ( Row != qNIL ) {
        XHTML << "<option value=\"" << Ids(Row) << "\" ";

        if ( Ids(Row) == Id ) {
          Available = true;
          XHTML << " selected=\"true\"";
        }

        XHTML <<  " disabled=\"true\">" << Names(Row) << " (" << Ids(Row) << ")" << "</option>" << txf::nl;
        Row = Ids.Next(Row);
      }

      return Available;
    }
  }

  bso::sBool Fill_(
    const str::dString  &Id,
    const str::dStrings &Ids,
    const str::dStrings &Names,
    str::dString &XHTML)
  {
    bso::sBool Available = false;
  qRH;
    flx::rStringWDriver SDriver;
    txf::rWFlow TFlow;
  qRB;
    SDriver.Init(XHTML);
    TFlow.Init(SDriver);
    Available = Fill_(Id, Ids, Names, TFlow);
  qRR;
  qRT;
  qRE;
    return Available;
  }

  bso::sBool FillMidiInDevices_(
    const str::dString &Id,
    str::dString &XHTML)
  {
    bso::sBool Available = false;
  qRH;
    str::wStrings Ids, Names;
  qRB;
    tol::Init(Ids, Names);

    mscmdd::GetMidiInDeviceNames(Ids, Names);

    Available = Fill_(Id, Ids, Names, XHTML);
  qRR;
  qRT;
  qRE;
    return Available;
  }

  bso::sBool FillMidiOutDevices_(
    const str::dString &Id,
    str::dString &XHTML)
  {
    bso::sBool Available = false;
  qRH;
    str::wString Id;
    str::wStrings Ids, Names;
  qRB;
    tol::Init(Id, Ids, Names);
    midiq::GetDeviceInId(Id);

    mscmdd::GetMidiOutDeviceNames(Ids, Names);

    Available = Fill_(Id, Ids, Names, XHTML);
  qRR;
  qRT;
  qRE;
    return Available;
  }
}

#define D_( name )\
  namespace actions_ {\
    SCLX_ADec( sSession, name );\
  }\
  SCLX_ADef( sSession, actions_, name )

namespace {
  namespace {
    bso::sBool Display_(
      const melody::rXMelody &XMelody,
      main::sSession &Session)
    {
      bso::sBool Success = false;
    qRH;
      str::wString ABC, Script;
      bso::sS8 OctaveOverflow = 0;
      bso::pInt Buffer;
    qRB;
      tol::Init(ABC, Script);

      OctaveOverflow = mscabc::Convert(XMelody, XMelody.Accidental, Session.Width, true, ABC);

      if ( false && ( OctaveOverflow != 0 ) )
        Session.AlertB("Octave error !!!");
      else {
        Script.Init();
        flx::rStringTOFlow(Script) << "renderABC(\"" << ABC << "\");" << "highlightNote(\"" << ( Session.Row == qNIL ? "" : bso::Convert(*Session.Row, Buffer) ) << "\");" << "updatePlayer();";

        Session.Execute(Script);

        Success = true;
      }
    qRR;
    qRT;
    qRE;
      return Success;
    }
  }

  namespace _ {
    void GetScriptsXHTML(
      const str::dStrings &Ids,
      txf::sWFlow &XHTML)
      {
      qRH;
        str::wString Label, Description;
        sdr::sRow Row = qNIL;
      qRB;
        Row = Ids.First();

        while ( Row != qNIL ) {
          tol::Init(Label, Description);

          registry::GetScriptFeature(Ids(Row), Label, Description);

          XHTML << "<button xdh:mark=\"" << Ids(Row) << "\" xdh:onevent=\"Execute\">" << Label << "</button>" << txf::nl;

          Row = Ids.Next(Row);
        }
      qRR;
      qRT;
      qRE;
      }
  }

  void GetScriptsXHTML_(str::wString &XHTML)
  {
  qRH;
    str::wStrings Ids;
    flx::rStringTWFlow Flow;
  qRB;
    Ids.Init();
    Flow.Init(XHTML);

    registry::GetScriptIds(Ids);
    _::GetScriptsXHTML(Ids, Flow);
  qRR;
  qRT;
  qRE;
  }
}

namespace {
  void UpdateUIWidth_(
    const str::dString &Value,
    sSession &Session)
    {
    qRH;
      rTValues_ Values;
    qRB;
      Values.Init();

      Values.Add(iWidthRangeInput, Value);
      Values.Add(iWidthNumberInput, Value);

      Session.SetValues(Values);
    qRR;
    qRT;
    qRE;
  }

  bso::sBool SetUI_(
    const melody::rXMelody &XMelody,
    sSession &Session)
    {
      bso::sBool MidiInAvailable = false;
    qRH;
      str::wString XHTML, Device;
      mscmld::eAccidental Accidental = mscmld::a_Undefined;
      bso::pInt IBuffer;
      qCBUFFERh CBuffer;
      rTValues_ Values;
    qRB;
      XHTML.Init();

      Values.Init();

      if ( ( MidiInAvailable = FillMidiInDevices_(Device, XHTML) ) )
        Session.RemoveAttribute(Session.Parent("beautiful-piano", CBuffer), "open");
      else
        Values.Add(iMidiIn, "None");

      Session.End(L_( iMidiIn ), XHTML);

      /*
      XHTML.Init();
      FillMidiOutDevices_(XHTML);
      Session.Inner("MidiOut", XHTML);
      */

      Values.Add(iAccidentalAmount, abs(XMelody.Signature.Key));

      Accidental = XMelody.Signature.Key ? XMelody.Signature.Key > 0 ? mscmld::aSharp : mscmld::aFlat : XMelody.Accidental;
      Values.Add(iAccidental, mscmld::GetLabel(Accidental));

      Values.Add(iNumerator, XMelody.Signature.Time.Numerator());
      Values.Add(iDenominator, XMelody.Signature.Time.Denominator());

      Values.Add(iOctave, Session.BaseOctave);

      Session.SetValues(Values);

      UpdateUIWidth_(bso::Convert(Session.Width, IBuffer), Session);

      XHTML.Init();
      GetScriptsXHTML_(XHTML);
      Session.End(L_( iScripts ), XHTML);
    qRR;
    qRT;
    qRE;
      return MidiInAvailable;
    }
}

D_( OnNewSession )
{
qRH;
  melody::hGuard Guard;
  str::wString Body;
qRB;
  Session.Width = sclm::MGetU8(registry::parameter::Width, WidthMax);

  if ( Session.Width < WidthMin )
    sclr::ReportBadOrNoValueForEntryErrorAndAbort(registry::parameter::Width);

  Session.BaseOctave = sclm::MGetU8(registry::parameter::BaseOctave, BaseOctaveMax);

  Body.Init();
  sclm::MGetValue(registry::definition::Body, Body);

  Session.Inner(str::Empty, Body);

  CXMEL();
  Session.MidiIn = SetUI_(XMelody, Session) ? dsAvailaible : dsUnavailable;

  Session.Execute("createStylesheet();");

  Session.Execute("activate()");
qRR;
qRT;
qRE;
}

namespace {
  void UpdateUI_(
    sSession &Session,
    const melody::rXMelody &XMelody)
  {
  qRH;
    sIds_ Ids;
  qRB;
    Ids.Init(); // First contains ids of element which had to be disabled!

    if ( !XMelody.Exists(Session.Row) )
      Session.Row = XMelody.Last();

    if ( Session.Row == qNIL )
      Ids.Put(Navigation_, Removing_);
    else {
      if ( Session.Row == XMelody.First() )
        Ids.Put(iFirst, iPrevious);
      if ( Session.Row == XMelody.Last() )
        Ids.Put(iNext, iLast);
    }

    switch ( Session.MidiIn ) {
    case dsUnavailable:
      Ids.Put(iGrabMidiIn, iMidiIn);
      break;
    case dsAvailaible:
      break;
    case dsSelected:
      Ids.Put(iMidiIn);
      if ( IsMidiInOwner_(Session) )
        Ids.Put(iGrabMidiIn);
      break;
    default:
      qRGnr();
      break;
    }

    Session.Disable(Ids);

    Ids.Invert(All_);

    Session.Enable(Ids);

    Display_(XMelody, Session);
  qRR;
  qRT;
  qRE;
  }
}

D_( UpdateUI )
{
qRH;
  melody::hGuard Guard;
qRB;
  UpdateUI_(Session, melody::Get(Guard));
qRR;
qRT;
qRE;
}

D_( GrabMidiIn )
{
  GrabMidiIn_(Session);
}

D_( Hit )
{
qRH;
  str::wString Script;
  melody::hGuard Guard;
  mscmld::sNote Note;
qRB;
  Script.Init();
  flx::rStringTWFlow(Script) << "play(" << Id << ");";
  Session.Execute(Script);

  if ( IsMidiInOwner_(Session ) ) {
      XMEL();
      Note.Init(str::wString(Id).ToU8(), mscmld::sDuration(3), XMelody.Signature);

    if ( Session.Row == qNIL )
      Session.Row = XMelody.Append(Note);
    else {
      XMelody.InsertAt(Note, XMelody.Next(Session.Row) );
      Session.Row = XMelody.Next(Session.Row);
    }
  }
qRR;
qRT;
qRE;
}

namespace {
  void HandleKeyAndAccidental_(
    melody::rXMelody &XMelody,
    sSession &Session)
  {
  qRH;
    rValues_ Values;
    str::wString RawAccidental;
  qRB;
    tol::Init(Values, RawAccidental);

    Session.GetValues(sIds_(iAccidentalAmount, iAccidental), Values);

    Values.Get(iAccidental, RawAccidental);

    melody::HandleKeyAndAccidental(Values.Get<bso::sU8>(iAccidentalAmount), mscmld::GetAccidental(RawAccidental), XMelody);
  qRR;
  qRT;
  qRE;
  }
}

D_( SetAccidental )
{
qRH;
  melody::hGuard Guard;
qRB;
  XMEL();

  HandleKeyAndAccidental_(XMelody, Session);
qRR;
qRT;
qRE;
}


D_( SetAccidentalAmount )
{
qRH;
  melody::hGuard Guard;
qRB;
  XMEL();

  HandleKeyAndAccidental_(XMelody, Session);
qRR;
qRT;
qRE;
}

D_( Refresh )
{
  Session.Log("Refresh");
  main::MidiRFlow.reset();
}

D_( SelectNote )
{
qRH;
  melody::hGuard Guard;
qRB;
  str::wString(Id).ToNumber(*Session.Row);

  UpdateUI_(Session, melody::Get(Guard));
qRR;
qRT;
qRE;
}

D_( Rest )
{
qRH;
  melody::hGuard Guard;
qRB;
  XMEL();

  if ( Session.Row != qNIL ) {
    mscmld::sNote Note = XMelody(Session.Row);

    Note.Pitch = mscmld::pRest;
    Note.Duration.TiedToNext = false;

    XMelody.Store(Note, Session.Row);

    Session.Row = XMelody.Next(Session.Row);
  }
qRR;
qRT;
qRE;
}

D_( Duration )
{
qRH;
  melody::hGuard Guard;
qRB;
  XMEL();

  if ( Session.Row != qNIL ) {
    mscmld::sNote Note = XMelody(Session.Row);

    str::wString(Id).ToNumber(Note.Duration.Base);

    XMelody.Store(Note, Session.Row);

    if ( Session.Row != XMelody.Last() )
      Session.Row = XMelody.Next(Session.Row);
  }
qRR;
qRT;
qRE;
}

D_( Dot )
{
qRH;
  melody::hGuard Guard;
qRB;
  XMEL();

  if ( Session.Row != qNIL ) {
    mscmld::sNote Note = XMelody(Session.Row);

    if ( Note.Duration.Modifier >= 3 )
      Note.Duration.Modifier = 0;
    else
      Note.Duration.Modifier++;

    XMelody.Store(Note, Session.Row);
  }
qRR;
qRT;
qRE;
}

D_( Tie )
{
qRH;
  melody::hGuard Guard;
qRB;
  XMEL();

  if ( Session.Row != qNIL ) {
    mscmld::sNote Note = XMelody(Session.Row);

    if ( Note.Pitch != mscmld::pRest ) {
      if ( Note.Duration.TiedToNext ) {
        Note.Duration.TiedToNext = false;
        XMelody.Store(Note, Session.Row);
        XMelody.Remove(XMelody.Next(Session.Row));
      } else {
        Note.Duration.TiedToNext = true;
        XMelody.Store(Note, Session.Row);
        Note.Duration.TiedToNext = false;
        Note.Duration.Modifier = 0;
        Note.Duration.Base = 3;

        mscmld::sRow Row = XMelody.Next(Session.Row);

        if ( Row == qNIL )
          XMelody.Append(Note);
        else
          XMelody.InsertAt(Note, Row);
      }
    }
  }
qRR;
qRT;
qRE;
}

namespace {
  void ToXML_(
    const mscmld::dMelody &Melody,
    mscmld::eAccidental Accidental,
    txf::sWFlow &Flow)
  {
  qRH;
    xml::rWriter Writer;
    xtf::sPos Pos;
  qRB;
    Writer.Init(Flow, xml::oIndent, xml::e_Default);
//  Writer.GetFlow() << "<?xml-stylesheet type='text/xsl' href='data:text/xsl;base64,PD94bWwgdmVyc2lvbj0iMS4wIj8+CjwhLS0gY29weS1vZi54c2wgLS0+Cjx4c2w6c3R5bGVzaGVldCB2ZXJzaW9uPSIxLjAiCiAgeG1sbnM6eHNsPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L1hTTC9UcmFuc2Zvcm0iPgoKICA8eHNsOnRlbXBsYXRlIG1hdGNoPSIvIj4KICAgIDx4c2w6Y29weS1vZiBzZWxlY3Q9IioiLz4KICA8L3hzbDp0ZW1wbGF0ZT4KPC94c2w6c3R5bGVzaGVldD4=' ?>\n";

    Writer.PushTag("Melody");
    Writer.PutAttribute("Amount", Melody.Amount() );

    mscmld::WriteXML(Melody, Accidental, Writer);

    Writer.PopTag();
  qRR;
  qRT;
  qRE;
  }

  void ToXML_(
    const melody::rXMelody &XMelody,
    txf::sWFlow &Flow)
  {
    ToXML_(XMelody, XMelody.Accidental, Flow);

    Flow << txf::nl;  // Without this, with an empty melody the root 'Melody' will not be available for the script.
  }
}

namespace {
  qCDEFC(ABCBuiltInScriptId_, "_ABC");

  void ToBase64ABC_(
    const melody::rXMelody &XMelody,
    sWidth Width,
    txf::sWFlow &Flow)
    {
    qRH;
      cdgb64::rEncodingWFlow B64Flow;
      txf::sWFlow B64TWFlow;
    qRB;
      B64Flow.Init(Flow.Flow(), cdgb64::fURL);
      B64TWFlow.Init(B64Flow);

      mscabc::Convert(XMelody, XMelody.Accidental, Width, false, B64TWFlow);
    qRR;
    qRT;
    qRE;
    }
}

D_( Execute )
{
qRH;
	str::wString Mark, Script, Mime;
	flx::rExecDriver XDriver;
	txf::rWFlow WFlow;
	flw::rDressedRFlow<> RFlow;
	melody::hGuard Guard;
	flx::rStringTWFlow OFlow;
	str::wString Output;
	qCBUFFERh Buffer;
	int C;
	bso::sBool EmbedScriptResult = false;
qRB;
  EmbedScriptResult = Session.GetBoolValue(L_( iEmbedded ));

  tol::Init(Mark, Script, Mime);
  Session.GetMark(Id, Mark);
	registry::GetScriptContentAndMime(Mark, Script, Mime);

	Script.Append(";echo -n '$';");

  Output.Init();
  OFlow.Init(Output);

  if ( !EmbedScriptResult )
    OFlow << "window.open().document.write('";

  OFlow << "<iframe src=\"data:" << Mime << ";base64,";

	if ( Mark == ABCBuiltInScriptId_ )
    ToBase64ABC_(melody::Get(Guard), Session.Width, OFlow);
  else {
    XDriver.Init(Script);
    WFlow.Init(XDriver);

    ToXML_(melody::Get(Guard), WFlow);

    WFlow.Commit();

    RFlow.Init(XDriver);

    while ( ( C = RFlow.Get() ) != '$' ) {
      if ( isgraph(C) )
        OFlow << (char)C;
    }
  }

	OFlow << "\" frameborder=\"0\" style=\"border: 0; top: 0px; left: 0px; bottom: 0px; right: 0px; width: 100%; height: ";

	if ( EmbedScriptResult )
    OFlow << "400px";
  else
    OFlow << "100%";

  OFlow <<  ";\" allowfullscreen></iframe>";

	if ( !EmbedScriptResult)
    OFlow << "');";

	OFlow.reset();

	if ( EmbedScriptResult ) {
    Session.Inner(L_( iOutput ), Output);
    Session.Execute("resizeOutputIFrame();");
    Session.SetAttribute(Session.Parent("Output", Buffer), "open", "true");
    Session.ScrollTo(L_( iOutput ));
  } else
    Session.Execute(Output);
qRR;
qRT;
qRE;
}

D_( First )
{
qRH;
  melody::hGuard Guard;
qRB;
  CXMEL();

  if ( Session.Row != XMelody.First() ) {
    Session.Row = XMelody.First();

    UpdateUI_(Session, XMelody);
  }
qRR;
qRT;
qRE;
}

D_( Previous )
{
qRH;
  melody::hGuard Guard;
qRB;
  CXMEL();

  if ( Session.Row != XMelody.First() ) {
    Session.Row = XMelody.Previous(Session.Row);

    UpdateUI_(Session, XMelody);
  }
qRR;
qRT;
qRE;
}

D_( Next )
{
qRH;
  melody::hGuard Guard;
qRB;
  CXMEL();

  if ( Session.Row != XMelody.Last() ) {
    Session.Row = XMelody.Next(Session.Row);

    UpdateUI_(Session, XMelody);
  }
qRR;
qRT;
qRE;
}

D_( Last )
{
qRH;
  melody::hGuard Guard;
qRB;
  CXMEL();

  if ( Session.Row != XMelody.Last() ) {
    Session.Row = XMelody.Last();

    UpdateUI_(Session, XMelody);
  }
qRR;
qRT;
qRE;
}

namespace {
  mscmld::sRow Delete_(
    mscmld::sRow Row,
    melody::rXMelody &XMelody)
  {
    bso::sBool IsLast = Row == XMelody.Last();

    XMelody.Remove(Row);

    if ( IsLast )
      Row = XMelody.Last();

    return Row;
  }
}

D_( Delete )
{
qRH;
  melody::hGuard Guard;
qRB;
  XMEL();

  if ( Session.Row != qNIL ) {
    Session.Row = Delete_(Session.Row, XMelody);
  }
qRR;
qRT;
qRE;
}

D_( Backspace )
{
qRH;
  melody::hGuard Guard;
qRB;
  XMEL();

  if ( Session.Row != XMelody.First() ) {
    Session.Row = Delete_(XMelody.Previous(Session.Row), XMelody);
  }
qRR;
qRT;
qRE;
}

D_( Clear )
{
qRH;
  melody::hGuard Guard;
qRB;
  XMEL();

  XMelody.wMelody::Init();
  Session.Row = qNIL;
qRR;
qRT;
qRE;
}

D_( Keyboard )
{
qRH;
  melody::hGuard Guard;
  str::wString Script;
  mscmld::sPitch Pitch;
  mscmld::sNote Note;
qRB;
  XMEL();

  Pitch = str::wString(Id+1).ToU8() + 5 + Session.BaseOctave * 12;

  Script.Init();
  flx::rStringTWFlow(Script) << "play(" << (bso::sUInt)Pitch << ");";

  Session.Execute(Script);

  Note.Init(Pitch, mscmld::sDuration(3), XMelody.Signature);

  if ( Session.Row == qNIL )
    Session.Row = XMelody.Append(Note);
  else {
    XMelody.InsertAt(Note, XMelody.Next(Session.Row) );
    Session.Row = XMelody.Next(Session.Row);
  }
qRR;
qRT;
qRE;
}

D_( SetTimeSignature )
{
qRH;
  rValues_ Values;
  melody::hGuard Guard;
  mscmld::sSignatureTime Signature;
qRB;
  Values.Init();
  Session.GetValues(sIds_(iNumerator, iDenominator), Values);

  Signature.Init(Values.Get<bso::sU8>(iNumerator), Values.Get<bso::sU8>(iDenominator));

  if ( !Signature.IsValid() )
    qRGnr();

  XMEL();

  XMelody.Signature.Time = Signature;
  mscmld::UpdateTimeSignature(Signature, XMelody);
qRR;
qRT;
qRE;
}

D_( SetOctave )
{
qRH;
  qCBUFFERh Buffer;
  melody::hGuard Guard;
  mscmld::sOctave BaseOctaveBackup = mscmld::UndefinedOctave;
qRB;
  XMEL();

  BaseOctaveBackup = Session.BaseOctave;

  str::wString(Session.GetValue(Id, Buffer)).ToNumber(Session.BaseOctave, str::sULimit<bso::sU8>(9));

  if ( !Display_(XMelody, Session) ) {
    bso::pInt Buffer;
    Session.BaseOctave = BaseOctaveBackup;
    Session.SetValue(L_( iOctave ), bso::Convert(Session.BaseOctave, Buffer));
  }
qRR;
qRT;
qRE;
}

D_( Test )
{
  Session.Log("Test");
}

D_( ChangeWidth )
{
qRH;
  str::wString Value;
  sWidth Width = 0;
  melody::hGuard Guard;
qRB;
  Value.Init();

  Session.GetValue(Id, Value);

  Value.ToNumber(Width, str::sULimit<sWidth>(WidthMax));

  if ( Width < WidthMin )
    qRGnr();

  UpdateUIWidth_(Value, Session);

  Session.Width = Width;

  Display_(melody::Get(Guard), Session);
qRR;
qRT;
qRE;
}

#undef L_
#define L_(name)  actions_::s##name::Label

void main::rActionHelper::SCLXOnAfterAction(
  sSession &Session,
  const char *Id,
  const char *Action)
{
  if ( strcmp(L_( UpdateUI ), Action ) )
    sclx::Broadcast(L_( UpdateUI ));
}

namespace {
  using namespace actions_;

  namespace _ {
    template <typename action> void Add(
      rCore &Core,
      action &Action )
    {
        Core.Add(Action.Label, Action);
    }

    template <typename action, typename... actions> void Add(
      rCore &Core,
      action &Action,
      actions &...Actions)
    {
        Add(Core, Action);
        Add(Core, Actions...);
    }
  }

  void RegisterActions_(void)
  {
    _::Add(Core,
      OnNewSession, UpdateUI, Hit, GrabMidiIn, SetAccidental, SetAccidentalAmount, Refresh,
      SelectNote, Rest, Duration, Dot, Tie,
      Execute, First, Previous, Next, Last, Delete, Backspace, Clear,
      Keyboard, Test, SetTimeSignature, SetOctave, ChangeWidth );
  }
}

#define R_( name ) Add_(main::Core, actions_::name)


qGCTOR( main ) {
  Core.Init();
  RegisterActions_();
  InitializeMidiInOwning_();
  ActionHelper.Init();

  // ActionHelper.Before.Add();
  ActionHelper.After.Add(L_( UpdateUI ), L_( SelectNote ), L_( First ), L_( Previous ), L_( Next ), L_( Last ), L_( SetOctave ), L_( ChangeWidth ));
}
