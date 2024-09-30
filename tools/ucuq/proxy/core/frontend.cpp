/*
  Copyright (C) 2024 Claude SIMON (http://q37.info/contact/).

  This file is part of the 'UCUq' tool.

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
    bso::sBool *IsAlive)
  {
    bso::sU8 Answer = a_Undefined;

    common::Get(Flow, Answer, IsAlive);

    if ( (Answer > a_amount) || (Answer == aDisconnected) )
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
    bso::sBool *BackendIsAlive)
  {
    bso::sBool Cont = true;
   qRH;
    str::wString Returned;
  qRB;
    common::Put(rPing, Backend, BackendIsAlive);
    common::Commit(Backend, BackendIsAlive);

    switch ( GetAnswer_(Backend, BackendIsAlive) ) {
    case aOK:
      Returned.Init();
      common::Get(Backend, Returned, BackendIsAlive);
      common::Put(aOK, Frontend);
      common::Put(Returned, Frontend);
      break;
    case aPuzzled:
      Returned.Init();
      common::Get(Backend, Returned, BackendIsAlive);
      common::Put(aPuzzled, Frontend);
      common::Put(Returned, Frontend);
    default:
      qRGnr();
      break;
    }
  qRR;
    if ( (BackendIsAlive != NULL) && !BackendIsAlive ) {
      common::Put(aDisconnected, Frontend);
      Cont = false;
      qRRst();
    }
  qRT;
  qRE;
    return Cont;
  }

  bso::sBool HandleExecute_(
    flw::rRWFlow &Frontend,
    flw::rRWFlow &Backend,
    bso::sBool *BackendIsAlive)
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

    common::Put(rExecute, Backend, BackendIsAlive);
    common::Put(Script, Backend, BackendIsAlive);
    common::Put(Expression, Backend, BackendIsAlive);
    common::Commit(Backend, BackendIsAlive);

    switch ( GetAnswer_(Backend, BackendIsAlive) ) {
    case aOK:
      Returned.Init();
      common::Get(Backend, Returned, BackendIsAlive);
      common::Put(aOK, Frontend);
      common::Put(Returned, Frontend);
      common::Commit(Frontend);
      break;
    case aError:
      Returned.Init();
      common::Get(Backend, Returned, BackendIsAlive);
      common::Put(aError, Frontend);
      common::Put(Returned, Frontend);
      common::Commit(Frontend);
      break;
    case aPuzzled:
      Returned.Init();
      common::Get(Backend, Returned, BackendIsAlive);
      common::Put(aPuzzled, Frontend);
      common::Put(Returned, Frontend);
      break;
    default:
      qRGnr();
      break;
    }
  qRR;
    if ( (BackendIsAlive != NULL) && !BackendIsAlive ) {
      common::Put(aDisconnected, Frontend);
      Cont = false;
      qRRst();
    }
  qRT;
  qRE;
    return Cont;
  }
}

void frontend::Process(fdr::rRWDriver &Driver)
{
qRH;
  backend::sRow Row = qNIL;
  flw::rDressedRWFlow<> Backend;
  flw::rDressedRWFlow<> Frontend;
  str::wString Message, Command;
  backend::wSelector Selector;
  bso::sBool BackendIsAlive = false;
qRB;
  Frontend.Init(Driver);

  Selector.Init();
  common::Get(Frontend, Selector.Token);
  common::Get(Frontend, Selector.Id);

  Row = backend::Get(Selector, &BackendIsAlive);

  Frontend.Init(Driver);

  if ( Row == qNIL ) {
    Message.Init();
    messages::GetTranslation(messages::iNoBackendWithGivenTokenAndId, Message, Selector.Token, Selector.Id);
    common::Put(Message, Frontend);
    common::Commit(Frontend);
  } else {
    common::Put("", Frontend);
    common::Commit(Frontend);

    Backend.Init(backend::Get(Row));

    while ( !Frontend.EndOfFlow() ) {
      switch ( GetRequest_(Frontend) ) {
      case rExecute:
        if ( !HandleExecute_(Frontend, Backend, &BackendIsAlive) )
          break;
        break;
      case rPing:
        if ( !HandlePing_(Frontend, Backend, &BackendIsAlive) )
          break;
        break;
      default:
        qRGnr();
        break;
      }
      common::Dismiss(Backend, &BackendIsAlive);
    }

    Backend.reset(false); // The corresponding driver is already destroyed!
   }
  qRR;
  qRT;
  qRE;
}
