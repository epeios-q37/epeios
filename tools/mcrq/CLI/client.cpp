/*
	Copyright (C) 2021 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'McRq' tool.

    'McRq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'McRq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'McRq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "client.h"

#include "registry.h"

#include "sclm.h"

using namespace client;

namespace {
  namespace protocol_ {
    qCDEF(char *, Id, "2e9e85ea-342f-4e1e-b263-0fd9c7118e35");
    qCDEF(csdcmn::sVersion, LastVersion, 0);
  }
}

namespace {
  class sProcessing_
  : public common::cProcessing
  {
  private:
    qRMV(server::rHandler, S_, Server_);
  protected:
    virtual common::eAction COMMONProcess(flw::rRWFlow &Client)
    {
      common::eAction Action = common::a_Undefined;
    qRH;
      server::sRow Row = qNIL;
      flw::rDressedRWFlow<> Server;
      str::wString Command;
    qRB;
      Row = S_().Get();

      if ( Row != qNIL ) {
        Server.Init(S_().Get(Row));

        while ( !Client.EndOfFlow() ) {
          Command.Init();

          common::Get(Client, Command);
          common::Put(Command, Server);

          Server.Commit();
        }
      }

      Action = common::aStopAndDelete;
    qRR;
    qRT;
    qRE;
      return Action;
    }
  public:
    void reset(bso::sBool P = true)
    {
      Server_ = NULL;
    }
    qCDTOR(sProcessing_);
    void Init(server::rHandler &Server)
    {
      reset();

      Server_ = &Server;
    }
  } Processing_;
}

void client::rHandler::Process(void)
{
  return rHandler_::Process(sclm::MGetU16(registry::parameter::client::Service), protocol_::Id, protocol_::LastVersion, common::tClient, Processing_);
}

void client::Set(server::rHandler &Server)
{
  Processing_.Init(Server);
}
