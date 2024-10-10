/*
  Copyright (C) 2024 Claude SIMON (http://q37.info/contact/).

  This file is part of the 'UCUq' toolkit.

  'UCUq' is free software: you can redistribute it and/or modify it
  under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  'UCUq' is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with 'UCUq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "manager.h"

#include "backend.h"
#include "messages.h"
#include "frontend.h"

#include "ucumng.h"

#include "flw.h"
#include "str.h"

using namespace manager;

namespace {
  void Close_(flw::rRWFlow &Manager)
  {
  qRH;
    str::string Token;
  qRB;
    Token.Init();
    ucucmn::Get(Manager, Token);
    ucucmn::Dismiss(Manager);

    backend::Withdraw(Token);
  qRR;
  qRT;
  qRE;
  }


 void Execute_(
    flw::rRWFlow &Manager,
    const fdr::rRWDriver &Driver)
  {
  qRH;
    flw::rDressedRWFlow<> Backend;
    backend::wSelector Selector;
    str::wString Script, Expression, Message, Response;
    common::rCaller *Caller = NULL;
    bso::sBool Cont = true;
    common::gTracker Tracker;
  qRB;
    tol::Init(Selector, Script, Expression);

    common::Get(Manager, Selector.Token);
    common::Get(Manager, Selector.Id);
    common::Get(Manager, Script);
    common::Get(Manager, Expression);

    Caller = backend::Hire(Selector, &Driver);

    if ( Caller == NULL ) {
      Message.Init();

      messages::GetTranslation(messages::iNoBackendWithGivenTokenAndId, Message, Selector.Token, Selector.Id);

      common::Put(ucumng::aError, Manager);
      common::Put(Message, Manager);
      common::Commit(Manager);
    } else {
      Tracker.Caller = Caller;
      Tracker.Candidate = &Driver;

      Backend.Init(*Caller->GetDriver());

      common::Put(backend::rExecute, Backend, &Tracker);
      common::Put(Script, Backend, &Tracker);
      common::Put(Expression, Backend, &Tracker);
      common::Commit(Backend, &Tracker);

      switch ( backend::GetAnswer(Backend, &Tracker) ) {
      case backend::aOK:
        Response.Init();

        common::Get(Backend, Response, &Tracker);
        common::Dismiss(Backend, &Tracker);

        common::Put(ucumng::aOK, Manager);
        common::Put(Response, Manager);

        common::Commit(Manager);
        break;
      case backend::aError:
      case backend::aPuzzled:
        Response.Init();

        common::Get(Backend, Response, &Tracker);
        common::Dismiss(Backend, &Tracker);

        common::Put(ucumng::aError, Manager);
        common::Put(Response, Manager);

        common::Commit(Manager);
        break;
      case backend::aDisconnected:
        common::Dismiss(Backend, &Tracker);
        break;
      default:
        qRGnr();
        break;
      }
    }
  qRR;
  qRT;
    if ( (Caller != NULL) && Caller->ShouldIDestroy(&Driver) ) {
      Backend.reset(false); // To avoid action on underlying driver which will be destroyed.
      qDELETE(Caller);
    }
  qRE;
  }

 void CreateVToken_(flw::rRWFlow &Manager)
 {
 qRH;
   str::wString
     Token,
     TrueToken,
     Id;
 qRB;
   tol::Init(Token, TrueToken);

   ucucmn::Get(Manager, Token);
   ucucmn::Get(Manager, TrueToken);
   ucucmn::Get(Manager, Id);

   ucucmn::Dismiss(Manager);

   backend::CreateVToken(Token, TrueToken, Id);

   ucucmn::Put(ucumng::aOK, Manager);

   ucucmn::Commit(Manager);
 qRR;
 qRT;
 qRE;
 }

 void DeleteVToken_(flw::rRWFlow &Manager)
 {
 qRH;
   str::wString Token;
 qRB;
   tol::Init(Token);

   ucucmn::Get(Manager, Token);

   ucucmn::Dismiss(Manager);

   backend::DeleteVToken(Token);

   ucucmn::Put(ucumng::aOK, Manager);

   ucucmn::Commit(Manager);
 qRR;
 qRT;
 qRE;
 }
}

void manager::Process(fdr::rRWDriver &Driver)
{
qRH;
  flw::rDressedRWFlow<> Flow;
  str::wString RawRequest;
qRB;
  Flow.Init(Driver);

  RawRequest.Init();
  ucucmn::Get(Flow, RawRequest);

  switch ( ucumng::GetRequest(RawRequest) ) {
  case ucumng::rClose_1:
    Close_(Flow);
    break;
  case ucumng::rExecute_1:
    Execute_(Flow, Driver);
    break;
  case ucumng::rCreateVToken_1:
    CreateVToken_(Flow);
    break;
  case ucumng::rDeleteVToken_1:
    DeleteVToken_(Flow);
    break;
  default:
    qRGnr();
    break;
  }
qRR;
qRT;
qRE;
}
