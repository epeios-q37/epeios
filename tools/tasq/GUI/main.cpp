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

#include "tsqxml.h"

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
    C_( DescriptionView );
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
}

#define L_(name)  GetLabel_(name)

namespace {
  qENUM( Mode_ ) {
    mView,
    mEdition,
    m_amount,
    m_Undefined
  };

  void SetDisplay_(
    eMode_ Mode,
    sSession &Session)
  {
  qRH;
    str::wStrings
      ViewIds, ViewClasses,
      EditionIds, EditionClasses,
      Ids;
  qRB;
    tol::Init(ViewIds, ViewClasses);

    ViewIds.AppendMulti(L_( iTree ), L_( iTitleView ), L_( iDescriptionView ), L_( iEdit ), L_( iNew ), L_( iDelete ));
    ViewClasses.AppendMulti(L_( cHide ), L_( cHide ), L_( cHide ), L_( cHide ), L_( cHide ), L_( cHide ));

    tol::Init(EditionIds, EditionClasses);

    EditionIds.AppendMulti(L_( iTitleEdition ), L_( iDescriptionEdition ), L_( iSubmit ), L_( iCancel ));
    EditionClasses.AppendMulti(L_( cHide ), L_( cHide ), L_( cHide ), L_( cHide ));

    switch( Mode ) {
    case mView:
      Session.AddClasses(EditionIds, EditionClasses);
      Session.RemoveClasses(ViewIds, ViewClasses);
      Session.Execute("markdown.toTextArea(); markdown = null;");
      break;
    case mEdition:
      Session.AddClasses(ViewIds, ViewClasses);
      Session.RemoveClasses(EditionIds, EditionClasses);
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
  void Select_(
    tsqtsk::sRow Row,
    const tsqtsk::dXTasks &Tasks,
    sSession &Session)
  {
  qRH;
    bso::pInteger Buffer;
    tsqtsk::sRow Looper = qNIL;
    qCBUFFERh Previous;
  qRB;
    Looper = Tasks.Parent(Row);

    while ( Looper != qNIL ) {
      Session.SetAttribute(Session.PreviousSibling(Session.PreviousSibling(bso::Convert(*Looper, Buffer), Previous), Previous), "checked", "true");

      Looper = Tasks.Parent(Looper);
    }

    Session.ScrollTo(bso::Convert(*Row, Buffer));

    Session.AddClass(Buffer(), L_( cSelected ));
  qRR;
  qRT;
  qRE;
  }
}

namespace {
  void Fill_(
    tsqtsk::sRow Row,
    const str::dString &Id,
    const rgstry::rTEntry &XSLEntry,
    const tsqbndl::dBundle &Bundle,
    sSession &Session)
  {
  qRH;
    str::wString XML;
    str::wString XSL, Base64XSL, XSLAsURI;
  qRB;
    XML.Init();

    if ( Row == qNIL )
      tsqxml::Write(Bundle, tsqxml::ffDisplay, XML);
    else
      tsqxml::Write(Row, Bundle, tsqxml::ffDisplay, XML);

    XSL.Init();
    sclm::MGetValue(XSLEntry, XSL);

    Base64XSL.Init();
    cdgb64::Encode(XSL, cdgb64::fOriginal, Base64XSL);

    XSLAsURI.Init("data:text/xml;base64,");
    XSLAsURI.Append(Base64XSL);

    XSL.StripLeadingChars('\n');
    Session.Inner(Id, XML, XSLAsURI);
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
  str::wString Body;
  str::wString Tree;
qRB;
  Body.Init();
  sclm::MGetValue(registry::definition::Body, Body);

  Session.Inner(str::Empty, Body);

  CBNDL();

  Fill_(qNIL, str::wString(L_( iTree )), registry::definition::XSLFiles::Items, Bundle, Session);

  SetDisplay_(mView, Session);
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
  bso::pInteger Buffer;
qRB;
  tol::Init(Title, Description);

  str::wString(Id).ToNumber(*Row);

  BNDL();

  if ( !Bundle.IsRoot(Row) )
    Bundle.Get(Row, Title, Description);

  Session.SetValue(L_( iTitleView ), Title);

  Script.Init();
  flx::rStringTWFlow(Script) << "renderMarkdown('DescriptionView','" << xdhcmn::Escape(Description, 0) << "');";
  Session.Execute(Script);

  Session.RemoveClass(bso::Convert(Session.Selected == qNIL ? *Bundle.RootTask() : *Session.Selected, Buffer), "selected");

  Session.AddClass(bso::Convert(*Row, Buffer), L_( cSelected ));

  Session.Selected = Row == Bundle.RootTask() ? qNIL : Row;

  SetDisplay_(mView, Session);
qRR;
qRT;
qRE;
}

namespace {
  void Edit_(
    const str::dString &Title,
    const str::dString &Description,
    bso::sBool SelectedIsRoot,
    sSession &Session)
  {
  qRH;
    str::wString Script, EscapedDescription;
  qRB;
    Session.SetValue(L_( iTitleEdition ), Title);

    tol::Init(Script, EscapedDescription);
    flx::rStringTWFlow(Script) << "markdown = editMarkdown('DescriptionEdition','" << xdhcmn::Escape(Description, EscapedDescription, 0) << "');";
    Session.Execute(Script);

    SetDisplay_(mEdition, Session);

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
  Edit_(str::Empty, str::Empty, Bundle.IsRoot(Session.Selected()), Session);
qRR;
qRT;
qRE;
}

D_( Edit )
{
qRH;
  BGRD;
  str::wString Title, Description;
qRB;
  CBNDL();

  tol::Init(Title, Description);
  Bundle.Get(Session.Selected(), Title, Description);

  Session.IsNew = false;
  Edit_(Title, Description, Bundle.IsRoot(Session.Selected()), Session);
qRR;
qRT;
qRE;
}

namespace {
  void RetrieveContent_(
    sSession &Session,
    str::dString &Title,
    str::dString &Description)
  {
    Session.GetValue(L_( iTitleEdition ), Title);
//    Session.Execute("let value = markdown.value(); markdown.toTextArea(); markdown = null; value;", Description);
    Session.Execute("markdown.value();", Description);
  }
}

D_( Cancel )
{
qRH;
  BGRD;
  str::wString NewTitle, OldTitle, NewDescription, OldDescription;
qRB;
  tol::Init(NewTitle, OldTitle, NewDescription, OldDescription);

  RetrieveContent_(Session, NewTitle, NewDescription);

  if ( !Session.IsNew ) {
    CBNDL();

    Bundle.Get(Session.Selected(), OldTitle, OldDescription);
  }

  if ( ( OldTitle != NewTitle) || ( OldDescription != NewDescription ) ) {
    if ( Session.ConfirmB(str::wString("Are sure you want to cancel your modifications?")) )
      SetDisplay_(mView, Session);
  } else
    SetDisplay_(mView, Session);
qRR;
qRT;
qRE;
}

D_( Submit )
{
qRH;
  BGRD;
  str::wString Title, Description, XML;
  bso::pInteger Buffer;
qRB;
  tol::Init(Title, Description);

  RetrieveContent_(Session, Title, Description);

  Title.StripChars();

  if ( Title.Amount() == 0 ) {
    Session.AlertB(str::wString("Title can not be empty!"));
    Session.Focus(L_( iTitleEdition ));
  } else {
    BNDL();

    if ( Session.IsNew ) {
      Session.Selected = Bundle.Add(Title, Description, Session.Selected());

      Fill_(qNIL, str::wString(L_( iTree )), registry::definition::XSLFiles::Items, Bundle, Session);

      Select_(Session.Selected, Bundle.Tasks, Session);
      Session.IsNew = false;
    } else {
      Bundle.Set(Title, Description, Session.Selected());

      Session.SetValue(bso::Convert(*Session.Selected, Buffer), Title);
    }

    SetDisplay_(mView, Session);
  }
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
      Submit, Cancel);
  }
}

#define R_( name ) Add_(main::Core, actions_::name)

qGCTOR( main ) {
  Core.Init();
  Register_();
}
