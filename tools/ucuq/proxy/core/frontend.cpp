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


#include "frontend.h"

#include "registry.h"
#include "messages.h"
#include "backend.h"

#include "sclm.h"

#include "csdcmn.h"

using namespace frontend;

namespace {
  qENUM(Request_) { // Request issued by frontend (received as string)
    rPing_1,
    rExecute_1,
    r_amount,
    r_Undefined
  };

#define C( name )	case r##name : return #name; break

  const char *GetLabel_(eRequest_ Request)
  {
    switch ( Request ) {
      C(Ping_1);
      C(Execute_1);
    default:
      qRFwk();
      break;
    }

    return NULL;	// To avoid a warning.
  }

#undef C

    stsfsm::wAutomat FrontendRequestAutomat_;

    void FillFrontendRequestAutomat_(void)
    {
      FrontendRequestAutomat_.Init();
      stsfsm::Fill<eRequest_>(FrontendRequestAutomat_, r_amount, GetLabel_);
    }

  eRequest_ GetRequest_(const str::dString &Pattern)
  {
    return stsfsm::GetId(Pattern, FrontendRequestAutomat_, r_Undefined, r_amount);
  }

  eRequest_ GetRequest_(flw::rRFlow &Flow)
  {
    eRequest_ Request = r_Undefined;
  qRH;
    str::wString RawRequest;
  qRB;
    RawRequest.Init();

    common::Get(Flow, RawRequest);

    Request = GetRequest_(RawRequest);
  qRR;
  qRT;
  qRE;
    return Request;
  }

  bso::sBool HandlePing_(
    flw::rRWFlow &Frontend,
    flw::rRWFlow &Backend,
    common::gTracker *Tracker)
  {
    bso::sBool Cont = true;
   qRH;
    str::wString Returned;
  qRB;
    common::Put(backend::rPing, Backend, Tracker);
    common::Commit(Backend, Tracker);

    switch ( backend::GetAnswer(Backend, Tracker) ) {
    case backend::aOK:
      Returned.Init();
      common::Get(Backend, Returned, Tracker);
      common::Put(backend::aOK, Frontend);
      common::Put(Returned, Frontend);
      common::Commit(Frontend);
      break;
    case backend::aPuzzled:
      Returned.Init();
      common::Get(Backend, Returned, Tracker);
      common::Put(backend::aPuzzled, Frontend);
      common::Put(Returned, Frontend);
      common::Commit(Frontend);
      break;
    case backend::aDisconnected:
      Cont = false;
      break;
    default:
      qRGnr();
      break;
    }
  qRR;
  qRT;
  qRE;
    return Cont;
  }

  bso::sBool HandleExecute_(
    flw::rRWFlow &Frontend,
    flw::rRWFlow &Backend,
    const common::gTracker *Tracker)
  {
    bso::sBool Cont = true;
  qRH;
    str::wString
      Script,     // Script to execute.
      Expression, // Expression to evaluate which result if JSONified and returned.
      Returned;   // Result of the JSONified evaluation the expression, or exception description if an error occured.
  qRB;
    tol::Init(Script, Expression);

    common::Get(Frontend, Script);
    common::Get(Frontend, Expression);

    common::Put(backend::rExecute, Backend, Tracker);
    common::Put(Script, Backend, Tracker);
    common::Put(Expression, Backend, Tracker);
    common::Commit(Backend, Tracker);

    switch ( backend::GetAnswer(Backend, Tracker) ) {
    case backend::aOK:
      Returned.Init();
      common::Get(Backend, Returned, Tracker);
      common::Put(backend::aOK, Frontend);
      common::Put(Returned, Frontend);
      common::Commit(Frontend);
      break;
    case backend::aError:
      Returned.Init();
      common::Get(Backend, Returned, Tracker);
      common::Put(backend::aError, Frontend);
      common::Put(Returned, Frontend);
      common::Commit(Frontend);
      break;
    case backend::aPuzzled:
      Returned.Init();
      common::Get(Backend, Returned, Tracker);
      common::Put(backend::aPuzzled, Frontend);
      common::Put(Returned, Frontend);
      break;
    case backend::aDisconnected:
      Cont = false;
      break;
    default:
      qRGnr();
      break;
    }
  qRR;
  qRT;
  qRE;
    return Cont;
  }
}

void frontend::Process(fdr::rRWDriver &Driver)
{
qRH;
  flw::rDressedRWFlow<> Backend;
  flw::rDressedRWFlow<> Frontend;
  str::wString Message, Command;
  backend::wSelector Selector;
  common::rCaller *Caller = NULL;
  bso::sBool Cont = true;
  common::gTracker Tracker;
qRB;
  Frontend.Init(Driver);

  Selector.Init();
  common::Get(Frontend, Selector.Token);
  common::Get(Frontend, Selector.Id);

  Caller = backend::Hire(Selector, &Driver);

  Frontend.Init(Driver);

  if ( Caller == NULL ) {
    Message.Init();
    messages::GetTranslation(messages::iNoBackendWithGivenTokenAndId, Message, Selector.Token, Selector.Id);
    common::Put(Message, Frontend);
    common::Commit(Frontend);
  } else {
    common::Put("", Frontend);
    common::Commit(Frontend);

    Tracker.Candidate = &Driver;
    Tracker.Caller = Caller;

    Backend.Init(*Caller->GetDriver());

    while ( !Frontend.EndOfFlow() && Cont ) {
      switch ( GetRequest_(Frontend) ) {
      case rExecute_1:
        if ( !HandleExecute_(Frontend, Backend, &Tracker) )
          break;
        break;
      case rPing_1:
        if ( !HandlePing_(Frontend, Backend, &Tracker) )
          break;
        break;
      default:
        qRGnr();
        break;
      }
      common::Dismiss(Backend, &Tracker);
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

qGCTOR(frontend)
{
  FillFrontendRequestAutomat_();
}
