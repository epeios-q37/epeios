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

sclx::action_handler<rSession> main::Core;

#define D_( name )\
  namespace actions_ {\
    SCLX_ADec( rSession, name );\
  }\
  SCLX_ADef( rSession, actions_, name )

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
    iMove,
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
    C_( Move );
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
  class gl_ {
  public:
    static const char *GetLabel(eId_ Id)
    {
      return ::GetLabel_(Id);
    }
  };

  typedef sclx::sIds<eId_, i_amount, gl_> sIds_;
  typedef sclx::rValues<eId_, i_amount, gl_> rValues_;
  typedef sclx::rTValues<eId_, i_amount, gl_> rTValues_;

  namespace _ {
    void HideShow(
      const sIds_ &Ids,
      rSession &Session,
      bso::sBool Hide)
    {
      if ( Hide )
        Session.AddClasses(Ids, L_( cHide ) );
      else
        Session.RemoveClasses(Ids, L_( cHide ) );
    }
  }

  void Hide_(
    const sIds_ &Ids,
    rSession &Session)
  {
    return _::HideShow(Ids, Session, true);
  }

  void Show_(
    const sIds_ &Ids,
    rSession &Session)
  {
    return _::HideShow(Ids, Session, false);
  }

  const sIds_ ViewIds_(iTitleView, iDescriptionView, iEdit, iNew, iDelete,  iMove);
  const sIds_ EditionIds_(iTitleEdition, iDescriptionEdition, iSubmit, iCancel, iTaskStatusEdition);
}


namespace {
  void GlobalDressing_(rSession &Session)
  {
  qRH;
    eState State = s_Undefined;
  qRB;
    State = Session.States.Top();

    switch( State ) {
    case sTaskView:
      Hide_(EditionIds_, Session);
      Show_(ViewIds_, Session);
      Session.Execute("markdown.toTextArea(); markdown = null;");
      break;
    case sTaskCreation:
    case sTaskModification:
      Show_(EditionIds_, Session);
      Hide_(ViewIds_, Session);
      break;
    default:
      qRGnr();
      break;
    }

    sIds_ Ids(iEdit, iDelete, iMove);

    if ( Session.Selected == qNIL )
      Session.Disable(Ids);
    else
      Session.Enable(Ids);
  qRR;
  qRT;
  qRE;
  }
}

namespace {
  void Unfold_(
    tsqtsk::sRow Row,
    const tsqtsk::dXTasks &Tasks,
    rSession &Session)
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
    rSession &Session)
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
    rSession &Session)
  {
  qRH;
    str::wString XML;
  qRB;
    XML.Init();

    if ( Row == qNIL )
      tsqxmlw::WriteAllTasks(Bundle, tsqxmlw::ffDisplay, XML);
    else
      tsqxmlw::WriteTask(Row, Bundle, tsqxmlw::ffDisplay, XML);

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

  Session.States.Push(sTaskView);

  Dress_(str::Empty, sclx::pInner, XML, registry::definition::Body, Session);

  CBNDL();

  DressTaskTree_(qNIL, L_( iTree ), sclx::pInner, registry::definition::XSLFiles::Items, Bundle, Session);

  GlobalDressing_(Session);
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

  GlobalDressing_(Session);
qRR;
qRT;
qRE;
}

namespace {
  void DressTaskStatusEdition_(
    tsqstts::sStatus Status,
    rSession &Session)
  {
  qRH;
    str::wStrings
      All,
      Displayed;
    str::wString Script;
    rTValues_ Values;
  qRB;
    All.Init(L_( iTaskTimelyFeatures), L_( iTaskEventFeatures), L_( iTaskRecurrentFeatures ));
    Values.Init();

    Values.Add(iTaskStatusType, (tsqstts::tType)Status.Type);

    switch( Status.Type ) {
    case tsqstts::tTimeless:
      Displayed.Init();
      break;
    case tsqstts::tTimely:
      Displayed.Init(L_( iTaskTimelyFeatures), L_( iTaskRecurrentFeatures ));
      Values.Add(iTaskTimelyDateLatest, Status.Timely.Latest, dte::fDDMMYYYY);
      Values.Add(iTaskTimelyDateEarliest, Status.Timely.Earliest, dte::fDDMMYYYY);
      break;
    case tsqstts::tEvent:
      Displayed.Init(L_( iTaskEventFeatures ), L_( iTaskRecurrentFeatures ));
      Values.Add(iTaskEventDate, Status.Event.Date, dte::fDDMMYYYY);
      if ( Status.Event.Time.IsSet() ) {
        Values.Add(iTaskEventTimeHour, Status.Event.Time.Hours());
        Values.Add(iTaskEventTimeMinute, Status.Event.Time.Minutes());
      }
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

    Values.Add(iTaskRecurrentSpan, Status.Recurrence.Span);
    Values.Add(iTaskRecurrentUnit, (tsqstts::tUnit)Status.Recurrence.Unit);
    Session.SetValues(Values);

    Session.RemoveClasses(Displayed, L_( cHide ));
  qRR;
  qRT;
  qRE;
  }

  void DressTaskEdition_(
    const str::dString &Title,
    const str::dString &Description,
    bso::sBool SelectedIsRoot,
    const tsqstts::sStatus &Status,
    rSession &Session)
  {
  qRH;
    str::wString Script, EscapedDescription;
  qRB;
    Session.SetValue(L_( iTitleEdition ), Title);

    tol::Init(Script, EscapedDescription);
    flx::rStringTWFlow(Script) << "markdown = editMarkdown('" << L_( iDescriptionEdition ) << "', '" << xdhcmn::Escape(Description, EscapedDescription, 0) << "');";
    Session.Execute(Script);

    DressTaskStatusEdition_(Status, Session);

    GlobalDressing_(Session);

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

  Session.States.Push(sTaskCreation);
  DressTaskEdition_(str::Empty, str::Empty, Bundle.IsRoot(Session.Selected()), tsqstts::sStatus(tsqstts::t_Default), Session);
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

  Session.States.Push(sTaskModification);
  DressTaskEdition_(Title, Description, Bundle.IsRoot(Session.Selected()), Status, Session);
qRR;
qRT;
qRE;
}

namespace {
  void RetrieveContent_(
    rSession &Session,
    str::dString &Title,
    str::dString &Description,
    tsqstts::sStatus &Status)
  {
  qRH;
    rValues_ Values;
    tme::sHours Hours = 0;
    tme::sMinutes Minutes = 0;
    qCBUFFERh Buffer;
  qRB;
    Values.Init();

    Session.GetValues(sIds_(
      iTitleEdition, iTaskStatusType,
      iTaskEventDate, iTaskEventTimeHour, iTaskEventTimeMinute,
      iTaskTimelyDateLatest, iTaskTimelyDateEarliest,
      iTaskRecurrentSpan, iTaskRecurrentUnit),
      Values);

    Title.Append(Values.Get(iTitleEdition));

    Status.Type = (tsqstts::eType)Values.Get(iTaskStatusType).ToU8();

    switch( Status.Type ) {
    case tsqstts::tTimeless:
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
    default:
      qRGnr();
      break;
    }

    Values.Get(iTaskRecurrentSpan, Status.Recurrence.Span);
    Status.Recurrence.Unit = (tsqstts::eUnit)Values.Get<tsqstts::tUnit>(iTaskRecurrentUnit);

    Session.Execute("markdown.value();", Description);
  qRR;
  qRT;
  qRE;
  }
}

namespace {
  bso::sBool HasChanged_(
    const str::dString &NewTitle,
    const str::dString &NewDescription,
    const tsqstts::sStatus &NewStatus,
    tsqtsk::sRow Current,
    const tsqbndl::dBundle &Bundle)
  {
    bso::sBool HasChanged = false;
  qRH;
    str::wString CurrentTitle, CurrentDescription;
    tsqstts::sStatus CurrentStatus;
  qRB;
    tol::Init(CurrentTitle, CurrentDescription, CurrentStatus);

    if ( Current != qNIL )
      Bundle.Get(Current, CurrentTitle, CurrentDescription, CurrentStatus);

    HasChanged = ( CurrentTitle != NewTitle) || ( CurrentDescription != NewDescription ) || ( CurrentStatus != NewStatus );
  qRR;
  qRT;
  qRE;
    return HasChanged;
  }
}

D_( Cancel )
{
qRH;
  BGRD;
  str::wString Title, Description;
  tsqstts::sStatus Status;
qRB;
  tol::Init(Title, Description, Status);

  RetrieveContent_(Session, Title, Description, Status);

  CBNDL();

  if ( !HasChanged_(Title, Description, Status, ( Session.States.Top() != sTaskCreation ? Session.Selected() : qNIL ), Bundle )
       || Session.ConfirmB("Are sure you want to cancel your modifications?") ) {
      Session.States.Pop();
      GlobalDressing_(Session);
  }
qRR;
qRT;
qRE;
}

namespace {
  void HandleTaskCreation_(
    tsqtsk::sRow Parent,
    tsqtsk::sRow New,
    rSession &Session,
    tsqbndl::dBundle &Bundle)
  {
  qRH;
    bso::pInteger Buffer;
    qCBUFFERh IdBuffer;
  qRB;
    if ( Bundle.Tasks.ChildAmount(Parent == qNIL ? Bundle.RootTask() : Parent) == 1 ) {
      if ( Parent == qNIL ) {
        DressTaskTree_(qNIL, L_( iTree ), sclx::pInner, registry::definition::XSLFiles::Items, Bundle, Session);
        Session.AddClass(L_( iTree ), L_( cSelected ) );
      } else
        DressTaskTree_(Parent, Session.Parent(bso::Convert(*Parent, Buffer), IdBuffer), sclx::pInner, registry::definition::XSLFiles::Item, Bundle, Session);
    } else if ( Parent == qNIL ) {
      DressTaskTree_(New, Session.NextSibling(bso::Convert(*Bundle.RootTask(), Buffer), IdBuffer), sclx::pEnd, registry::definition::XSLFiles::Item, Bundle, Session);
    } else {
      DressTaskTree_(New, Session.NextSibling(bso::Convert(*Parent, Buffer), IdBuffer), sclx::pEnd, registry::definition::XSLFiles::Item, Bundle, Session);
    }

    Unfold_(New, Bundle.Tasks, Session);
  qRR;
  qRT;
  qRE;
  }
}

D_( Submit )
{
qRH;
  BGRD;
  str::wString Title, Description, XML;
  bso::pInteger Buffer;
  tsqstts::sStatus Status;
  rTValues_ Values;
qRB;
  tol::Init(Title, Description, Status);

  RetrieveContent_(Session, Title, Description, Status);

  Title.StripChars();

  if ( Title.Amount() == 0 ) {
    Session.AlertB("Title can not be empty!");
    Session.Focus(L_( iTitleEdition ));
  } else {
    BNDL();

    switch ( Session.State() ) {
    case sTaskCreation:
      HandleTaskCreation_(Session.Selected, Bundle.Add(Title, Description, Status, Session.Selected), Session, Bundle);
      break;
    case sTaskModification:
      Bundle.Set(Title, Description, Session.Selected);
      Values.Init();
      Values.Add(bso::Convert(*Session.Selected, Buffer), Title);
      Values.Add(iTitleView, Title);
      Values.Add(iDescriptionView, Description);
      Session.SetValues(Values);
      break;
    default:
      qRGnr();
      break;
    }

    Session.States.Pop();
    GlobalDressing_(Session);
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
      sclx::action_handler<rSession> &Core,
      action &Action )
    {
        Core.Add(Action.Name, Action);
    }

    template <typename action, typename... actions> void Add(
      sclx::action_handler<rSession> &Core,
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
