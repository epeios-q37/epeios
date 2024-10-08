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


#include "registry.h"

using namespace registry;

namespace parameter_ {
  rEntry Server_("Server", sclr::Parameters);
}

rEntry registry::parameter::server::Service("Service", parameter_::Server_);

namespace parameter_ {
  rEntry Client_("Client", sclr::Parameters);
}

rEntry registry::parameter::client::Service("Service", parameter_::Client_);


rEntry registry::definition::Notification("Notification", sclr::Definitions);