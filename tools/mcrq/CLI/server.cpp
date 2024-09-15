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


#include "server.h"

#include "registry.h"

#include "sclm.h"

using namespace server;

namespace {
  namespace protocol_ {
    qCDEF(char *, Id, "2b45ad37-2dcd-437c-9185-6ffbfcedfbbf");
    qCDEF(csdcmn::sVersion, LastVersion, 0);
  }
}

namespace {
  class sProcessing
    : public common::cProcessing
  {
  protected:
    virtual common::eAction COMMONProcess(flw::rRWFlow&) override
    {
      return common::aStopAndKeep;
    }
  } Processing_;
}

void server::rHandler::Process(void)
{
  sProcessing Processing;

	return rHandler_::Process(sclm::MGetU16(registry::parameter::server::Service), protocol_::Id, protocol_::LastVersion, common::tServer, Processing_);
}

sRow server::rHandler::Get(void) const
{
	return rHandler_::Get();
}

sck::rRWDriver& server::rHandler::Get(sRow Row)
{
  return rHandler_::Get(*Row);
}
