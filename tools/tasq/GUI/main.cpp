/*
  Copyright (C) 2022 Claude SIMON (http://zeusw.org/epeios/contact.html).

  This file is part of 'TASq' software.

  'TASq' is free software: you can redistribute it and/or modify it
  under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  'TASq' is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with 'TASq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "main.h"

#include "registry.h"

#include "tsqbndl.h"
#include "tsqxmlw.h"

using namespace main;

sclx::action_handler<sSession> main::Core;

#define D_( name )\
  namespace actions_ {\
    SCLX_ADec( sSession, name );\
  }\
  SCLX_ADef( sSession, actions_, name )

namespace {
  qENUM( Id_ ) {
    iTree,
    iTitleView,
    iTaskStatusEdition,
    iTaskStatusType,
    iTaskTimelyFeatures,
    iTaskTimelyDateLatest,
    iTaskTimelyDateEarliest,
    iTaskEventFeatures,
    iTaskEventDate,
    iTaskEventTime,
    iTaskEventTimeHour,
    iTaskEventTimeMinute,
    iTaskRecurrentFeatures,
    iTaskRecurrentSpan,
    iTaskRecurrentUnit,
    iDescriptionView,
    iNew,
    iEdit,
    iDelete,
    iTitleEdition,
    iDescriptionEdition,
    iSubmit,
    iCancel,
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
    C_( Tree );
    C_( TitleView );
    C_( TaskStatusEdition );
    C_( TaskStatusType );
    C_( TaskTimelyFeatures );
    C_( TaskTimelyDateLatest );
    C_( TaskTimelyDateEarliest );
    C_( TaskEventFeatures );
    C_( TaskEventDate );
    C_( TaskEventTime );
    C_( TaskEventTimeHour );
    C_( TaskEventTimeMinute );
    C_( DescriptionView );
    C_( TaskRecurrentFeatures);
    C_( TaskRecurrentSpan);
    C_( TaskRecurrentUnit);
    C_( New );
    C_( Edit );
    C_( Delete );
    C_( TitleEdition );
    C_( DescriptionEdition );
    C_( Submit );
    C_( Cancel );
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

  qENUM( Class_ ) {
    cSelected,
    cHide,
    c_amount,
    c_Undefined
  };

  const char *GetLabel_( eClass_ Class )
  {
    switch ( Class ) {
    case cSelected:
      return "selected";
      break;
    case cHide:
      return "hide";
      break;
    default:
      qRGnr();
      break;

    }

    return NULL;  // To avoid a warning.
  }

  qENUM( Attribute_ ) {
    aChecked,
    a_amount,
    a_Undefined
  };

  const char *GetLabel_(eAttribute_ Attribute)
  {
    switch ( Attribute ) {
    case aChecked:
      return "checked";
      break;
    default:
      qRGnr();
      break;
    }

    return NULL;  // To avoid a warning.
  }
}

#define L_(name)  GetLabel_(name)

namespace {
  qENUM( Mode_ ) {
    mView,
    mEdition,
    m_amount,
    m_Undefined
  };

  void GlobalDressing_(
    eMode_ Mode,
    sSession &Session)
  {
  qRH;
    str::wStrings ViewIds, EditionIds, Ids;

  qRB;
    ViewIds.Init(L_( iTree ), L_( iTitleView ), L_( iDescriptionView ), L_( iEdit ), L_( iNew ), L_( iDelete ));
    EditionIds.Init(L_( iTitleEdition ), L_( iDescriptionEdition ), L_( iSubmit ), L_( iCancel ), L_( iTaskStatusEdition));

    switch( Mode ) {
    case mView:
      Session.AddClasses(EditionIds, L_( cHide ));
      Session.RemoveClasses(ViewIds, L_( cHide ));
      Session.Execute("markdown.toTextArea(); markdown = null;");
      break;
    case mEdition:
      Session.AddClasses(ViewIds,  L_( cHide ));
      Session.RemoveClasses(EditionIds,  L_( cHide ));
      break;
    default:
      qRGnr();
      break;
    }

    Ids.Init();

    Ids.AppendMulti( L_( iEdit ), L_ ( iDelete ) );

    if ( Session.Selected == qNIL )
      Session.DisableElements( Ids );
    else
      Session.EnableElements( Ids );
  qRR;
  qRT;
  qRE;
  }
}

namespace {
  void Unfold_(
    tsqtsk::sRow Row,
    const tsqtsk::dXTasks &Tasks,
    sSession &Session)
  {
  qRH;
    bso::pInteger Buffer;
    qCBUFFERh Previous;
  qRB;
    while ( Row != qNIL ) {
      Session.SetAttribute(Session.PreviousSibling(Session.PreviousSibling(bso::Convert(*Row, Buffer), Previous), Previous), L_( aChecked ), "true");

      Row = Tasks.Parent(Row);
    }
  qRR;
  qRT;
  qRE;
  }
}

namespace {
  void Dress_(
    const str::dString &Id,
    sclx::ePosition Position,
    const str::dString &XML,
    const rgstry::rTEntry &XSLEntry,
    sSession &Session)
  {
  qRH;
    str::wString XSL, Base64XSL, XSLAsURI;
  qRB;
    XSL.Init();
    sclm::MGetValue(XSLEntry, XSL);

    Base64XSL.Init();
    cdgb64::Encode(XSL, cdgb64::fOriginal, Base64XSL);

    XSLAsURI.Init("data:text/xml;base64,");
    XSLAsURI.Append(Base64XSL);

    XSL.StripLeadingChars('\n');
    Session.Put(Id, Position, XML, XSLAsURI);
  qRR;
  qRT;
  qRE;
  }
}

namespace {
  void DressTaskTree_(
    tsqtsk::sRow Row,
    const str::dString &Id,
    sclx::ePosition Position,
    const rgstry::rTEntry &XSLEntry,
    const tsqbndl::dBundle &Bundle,
    sSession &Session)
  {
  qRH;
    str::wString XML;
  qRB;
    XML.Init();

    if ( Row == qNIL )
      tsqxmlw::Write(Bundle, tsqxmlw::ffDisplay, XML);
    else
      tsqxmlw::Write(Row, Bundle, tsqxmlw::ffDisplay, XML);

    Dress_(Id, Position, XML, XSLEntry, Session);
  qRR;
  qRT;
  qRE;
  }
}

#define BGRD  tsqbndl::hGuard BundleGuard
#define BNDL()  tsqbndl::dBundle &Bundle = tsqbndl::Get(BundleGuard)
#define CBNDL()  const tsqbndl::dBundle &Bundle = tsqbndl::CGet(BundleGuard)

D_( OnNewSession )
{
qRH;
  BGRD;
  str::wString XML;
qRB;
  XML.Init();
  tsqxmlw::WriteCorpus(XML);

  Dress_(str::Empty, sclx::pInner, XML, registry::definition::Body, Session);

  CBNDL();

  DressTaskTree_(qNIL, str::wString(L_( iTree )), sclx::pInner, registry::definition::XSLFiles::Items, Bundle, Session);

  GlobalDressing_(mView, Session);
qRR;
qRT;
qRE;
}

D_( Select )
{
qRH;
  BGRD;
  tsqtsk::sRow Row = qNIL;
  str::wString Title, Description, Script;
  tsqstts::sStatus Status;
  bso::pInteger Buffer;
qRB;
  tol::Init(Title, Description, Status);

  str::wString(Id).ToNumber(*Row);

  BNDL();

  if ( !Bundle.IsRoot(Row) )
    Bundle.Get(Row, Title, Description, Status);

  Session.SetValue(L_( iTitleView ), Title);

  Script.Init();
  flx::rStringTWFlow(Script) << "renderMarkdown('" << L_( iDescriptionView ) << "', '" << xdhcmn::Escape(Description, 0) << "');";
  Session.Execute(Script);

  Session.RemoveClass(bso::Convert(Session.Selected == qNIL ? *Bundle.RootTask() : *Session.Selected, Buffer), L_( cSelected ));

  Session.AddClass(bso::Convert(*Row, Buffer), L_( cSelected ));

  Session.Selected = Row == Bundle.RootTask() ? qNIL : Row;

  GlobalDressing_(mView, Session);
qRR;
qRT;
qRE;
}

namespace {
  typedef SCLX_TVALUESr(eId_, i_amount, GetLabel_) rTValues_;
}

namespace {
  void DressTaskStatusEdition_(
    tsqstts::sStatus Status,
    sSession &Session)
  {
  qRH;
    str::wStrings All;
    str::wString Displayed;
    str::wString Script;
    rTValues_ Values;
  qRB;
    All.Init(L_( iTaskTimelyFeatures), L_( iTaskEventFeatures), L_( iTaskRecurrentFeatures ));
    Values.Init();

    Values.Add(iTaskStatusType, (tsqstts::tType)Status.Type);

    switch( Status.Type ) {
    case tsqstts::tPending:
    case tsqstts::tCompleted:
      Displayed.Init();
      break;
    case tsqstts::tTimely:
      Displayed.Init(L_( iTaskTimelyFeatures));
      Values.Add(iTaskTimelyDateLatest, Status.Timely.Latest, dte::fDDMMYYYY);
      Values.Add(iTaskTimelyDateEarliest, Status.Timely.Earliest, dte::fDDMMYYYY);
      break;
    case tsqstts::tEvent:
      Displayed.Init(L_( iTaskEventFeatures ));
      Values.Add(iTaskEventDate, Status.Event.Date, dte::fDDMMYYYY);
      if ( Status.Event.Time.IsSet() ) {
        Values.Add(iTaskEventTimeHour, Status.Event.Time.Hours());
        Values.Add(iTaskEventTimeMinute, Status.Event.Time.Minutes());
      }
      break;
    case tsqstts::tRecurrent:
      Displayed.Init(L_( iTaskRecurrentFeatures ));
      Values.Add(iTaskRecurrentSpan, Status.Recurrent.Span);
      Values.Add(iTaskRecurrentUnit, (tsqstts::tUnit)Status.Recurrent.Unit);
      break;
    default:
      qRGnr();
      break;
    }

    Script.Init();

    switch ( Status.Type ) {
    case tsqstts::tEvent:
      flx::rStringTWFlow(Script) << "toDatePicker('" << L_( iTaskEventDate ) << "');";
      Session.Execute(Script);
      break;
    case tsqstts::tTimely:
      flx::rStringTWFlow(Script) << "toDatePicker('" << L_( iTaskTimelyDateLatest ) << "');" << "toDatePicker('" << L_( iTaskTimelyDateEarliest ) << "');";
      Session.Execute(Script);
      break;
    default:
      break;
    }

    Session.AddClasses(All, L_( cHide ));
    Values.Push(Session);
    Session.RemoveClass(Displayed, L_( cHide ));
  qRR;
  qRT;
  qRE;
  }

  void DressTaskEdition_(
    const str::dString &Title,
    const str::dString &Description,
    bso::sBool SelectedIsRoot,
    const tsqstts::sStatus &Status,
    sSession &Session)
  {
  qRH;
    str::wString Script, EscapedDescription;
  qRB;
    Session.SetValue(L_( iTitleEdition ), Title);

    tol::Init(Script, EscapedDescription);
    flx::rStringTWFlow(Script) << "markdown = editMarkdown('" << L_( iDescriptionEdition ) << "', '" << xdhcmn::Escape(Description, EscapedDescription, 0) << "');";
    Session.Execute(Script);

    DressTaskStatusEdition_(Status, Session);

    GlobalDressing_(mEdition, Session);

    Session.Focus(L_( iTitleEdition ));
  qRR;
  qRT;
  qRE;
  }
}

D_( New )
{
qRH;
  BGRD;
qRB;
  CBNDL();

  Session.IsNew = true;
  DressTaskEdition_(str::Empty, str::Empty, Bundle.IsRoot(Session.Selected()), tsqstts::sStatus(tsqstts::tPending), Session);
qRR;
qRT;
qRE;
}

D_( Edit )
{
qRH;
  BGRD;
  str::wString Title, Description;
  tsqstts::sStatus Status;
qRB;
  CBNDL();

  tol::Init(Title, Description, Status);
  Bundle.Get(Session.Selected(), Title, Description, Status);

  Session.IsNew = false;
  DressTaskEdition_(Title, Description, Bundle.IsRoot(Session.Selected()), Status, Session);
qRR;
qRT;
qRE;
}

namespace {
  typedef SCLX_VALUESr(eId_, i_amount, GetLabel_) rValues;
}

namespace {
  void RetrieveContent_(
    sSession &Session,
    str::dString &Title,
    str::dString &Description,
    tsqstts::sStatus &Status)
  {
  qRH;
    rValues Values;
    tme::sHours Hours = 0;
    tme::sMinutes Minutes = 0;
    tsqstts::tUnit Unit = tsqstts::u_Undefined;
    qCBUFFERh Buffer;
  qRB;
    Values.Init();

    Values.Fetch(Session,
      iTitleEdition, iTaskStatusType,
      iTaskEventDate, iTaskEventTimeHour, iTaskEventTimeMinute,
      iTaskTimelyDateLatest, iTaskTimelyDateEarliest,
      iTaskRecurrentSpan, iTaskRecurrentUnit);

    Title.Append(Values.Get(iTitleEdition));

    Status.Type = (tsqstts::eType)Values.Get(iTaskStatusType).ToU8();

    switch( Status.Type ) {
    case tsqstts::tPending:
      break;
    case tsqstts::tEvent:
      Values.Get(iTaskEventDate, Status.Event.Date, dte::fDDMMYYYY);

      Values.Get(iTaskEventTimeHour, Hours);
      Values.Get(iTaskEventTimeMinute, Minutes);
      Status.Event.Time.Init(Hours, Minutes);
      break;
    case tsqstts::tTimely:
      Values.Get(iTaskTimelyDateLatest, Status.Timely.Latest, dte::fDDMMYYYY);
      Values.Get(iTaskTimelyDateEarliest, Status.Timely.Earliest, dte::fDDMMYYYY);
      break;
    case tsqstts::tRecurrent:
      Values.Get(iTaskRecurrentSpan, Status.Recurrent.Span);

      Values.Get(iTaskRecurrentUnit, Unit);
      Status.Recurrent.Unit = (tsqstts::eUnit)Unit;
      break;
    case tsqstts::tCompleted:
      break;
    default:
      qRGnr();
      break;
    }

    Session.Execute("markdown.value();", Description);
  qRR;
  qRT;
  qRE;
  }
}

D_( Cancel )
{
qRH;
  BGRD;
  str::wString NewTitle, OldTitle, NewDescription, OldDescription;
  tsqstts::sStatus NewStatus, OldStatus;
qRB;
  tol::Init(NewTitle, OldTitle, NewDescription, OldDescription, NewStatus, OldStatus);

  RetrieveContent_(Session, NewTitle, NewDescription, NewStatus);

  if ( !Session.IsNew ) {
    CBNDL();

    Bundle.Get(Session.Selected(), OldTitle, OldDescription, OldStatus);
  }

  if ( ( OldTitle != NewTitle) || ( OldDescription != NewDescription ) || ( OldStatus != NewStatus ) ) {
    if ( Session.ConfirmB(str::wString("Are sure you want to cancel your modifications?")) )
      GlobalDressing_(mView, Session);
  } else
    GlobalDressing_(mView, Session);
qRR;
qRT;
qRE;
}

D_( Submit )
{
qRH;
  BGRD;
  str::wString Title, Description, XML;
  qCBUFFERh IdBuffer;
  bso::pInteger Buffer;
  tsqstts::sStatus Status;
qRB;
  tol::Init(Title, Description, Status);

  RetrieveContent_(Session, Title, Description, Status);

  Title.StripChars();

  if ( Title.Amount() == 0 ) {
    Session.AlertB(str::wString("Title can not be empty!"));
    Session.Focus(L_( iTitleEdition ));
  } else {
    BNDL();

    if ( Session.IsNew ) {
      tsqtsk::sRow
        Parent = Session.Selected,
        New = Bundle.Add(Title, Description, Status, Parent);

      if ( Bundle.Tasks.ChildAmount(Parent == qNIL ? Bundle.RootTask() : Parent) == 1 ) {
        if ( Parent == qNIL ) {
          DressTaskTree_(qNIL, str::wString(L_( iTree )), sclx::pInner, registry::definition::XSLFiles::Items, Bundle, Session);
          Session.AddClass(L_( iTree ), L_( cSelected ) );
        } else
          DressTaskTree_(Parent, str::wString(Session.Parent(str::wString(bso::Convert(*Parent, Buffer)), IdBuffer)), sclx::pInner, registry::definition::XSLFiles::Item, Bundle, Session);
      } else {
        DressTaskTree_(New, str::wString(Session.NextSibling(str::wString(bso::Convert(Parent == qNIL ? *Bundle.RootTask() : *Parent, Buffer)), IdBuffer)), sclx::pEnd, registry::definition::XSLFiles::Item, Bundle, Session);
      }

      Unfold_(New, Bundle.Tasks, Session);

      Session.IsNew = false;
    } else {
      Bundle.Set(Title, Description, Session.Selected);

      Session.SetValue(bso::Convert(*Session.Selected, Buffer), Title);
    }

    GlobalDressing_(mView, Session);
  }
qRR;
qRT;
qRE;
}

D_( SelectTaskType )
{
qRH;
  str::wString RawType;
qRB;
  RawType.Init();

  Session.GetValue(Id, RawType);

  DressTaskStatusEdition_(tsqstts::sStatus((tsqstts::eType)RawType.ToU8()), Session);
qRR;
qRT;
qRE;
}

namespace {
  using namespace actions_;

  namespace _ {
    template <typename action> void Add(
      sclx::action_handler<sSession> &Core,
      action &Action )
    {
        Core.Add(Action.Name, Action);
    }

    template <typename action, typename... actions> void Add(
      sclx::action_handler<sSession> &Core,
      action &Action,
      actions &...Actions)
    {
        Add(Core, Action);
        Add(Core, Actions...);
    }
  }

  void Register_(void)
  {
    _::Add(Core,
      OnNewSession, Select,
      Edit, New,
      Submit, Cancel,
      SelectTaskType);
  }
}

#define R_( name ) Add_(main::Core, actions_::name)

qGCTOR( main ) {
  Core.Init();
  Register_();
}
