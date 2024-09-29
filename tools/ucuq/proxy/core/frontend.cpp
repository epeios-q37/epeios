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
    Frontend.Commit();
  } else {
    common::Put("", Frontend);
    Frontend.Commit();

    Backend.Init(backend::Get(Row));

    while ( !Frontend.EndOfFlow() ) {
      Command.Init();
      Frontend.Commit();

      common::Get(Frontend, Command);

      if ( !BackendIsAlive )
        break;

      common::Put(Command, Backend);

      Backend.Commit();
    }

    Backend.reset(false); // The corresponding driver is already destroyed!
  }
qRR;
qRT;
qRE;
}
