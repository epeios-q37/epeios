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
  str::wString Token, Message, Command;
qRB;
  Token.Init();

  Frontend.Init(Driver);
  common::Get(Frontend, Token);

  Row = backend::Get();

  Frontend.Init(Driver);

  if ( Row == qNIL ) {
    Message.Init();
    messages::GetTranslation(messages::iNoBackendWithGivenToken, Message, Token);
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
      common::Put(Command, Backend);

      Backend.Commit();
    }
  }
qRR;
qRT;
qRE;
}
