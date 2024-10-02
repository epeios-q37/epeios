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
  qENUM(Request_) {
    rPing,
    rExecute,
    r_amount,
    r_Undefined
  };

  qENUM(Answer_) {
    aOK,
    aError,
    aPuzzled,
    aDisconnected,  // For frontend only, not returned by backend
    a_amount,
    a_Undefined
  };

  eAnswer_ GetAnswer_(
    flw::rRFlow &Flow,
    const common::gTracker *Tracker)
  {
    bso::sU8 Answer = a_Undefined;

   common::Get(Flow, Answer, Tracker);

    if ( Answer > a_amount )
      qRGnr();

    return (eAnswer_)Answer;
  }

  eRequest_ GetRequest_(flw::rRFlow &Flow)
  {
    bso::sU8 Request = r_Undefined;

    common::Get(Flow, Request);

    if ( Request > a_amount )
      qRGnr();

    return (eRequest_)Request;
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
    common::Put(rPing, Backend, Tracker);
    common::Commit(Backend, Tracker);

    switch ( GetAnswer_(Backend, Tracker) ) {
    case aOK:
      Returned.Init();
      common::Get(Backend, Returned, Tracker);
      common::Put(aOK, Frontend);
      common::Put(Returned, Frontend);
      common::Commit(Frontend);
      break;
    case aPuzzled:
      Returned.Init();
      common::Get(Backend, Returned, Tracker);
      common::Put(aPuzzled, Frontend);
      common::Put(Returned, Frontend);
      common::Commit(Frontend);
      break;
    case aDisconnected:
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

    common::Put(rExecute, Backend, Tracker);
    common::Put(Script, Backend, Tracker);
    common::Put(Expression, Backend, Tracker);
    common::Commit(Backend, Tracker);

    switch ( GetAnswer_(Backend, Tracker) ) {
    case aOK:
      Returned.Init();
      common::Get(Backend, Returned, Tracker);
      common::Put(aOK, Frontend);
      common::Put(Returned, Frontend);
      common::Commit(Frontend);
      break;
    case aError:
      Returned.Init();
      common::Get(Backend, Returned, Tracker);
      common::Put(aError, Frontend);
      common::Put(Returned, Frontend);
      common::Commit(Frontend);
      break;
    case aPuzzled:
      Returned.Init();
      common::Get(Backend, Returned, Tracker);
      common::Put(aPuzzled, Frontend);
      common::Put(Returned, Frontend);
      break;
    case aDisconnected:
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
      case rExecute:
        if ( !HandleExecute_(Frontend, Backend, &Tracker) )
          break;
        break;
      case rPing:
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
