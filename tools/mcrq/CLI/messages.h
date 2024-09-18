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

#ifndef MESSAGES_INC_
# define MESSAGES_INC_

# include "tol.h"
# include "sclm.h"

namespace messages {
  qENUM(Id) {
    iClient,
    iServer,
    iUnknownProtocol, // %1: protocol ('Client'/'Server')
    iUnknownProtocolVersion, // %1: protocol
    iNoBackendWithGivenToken,  // %1: token
    i_amount,
    i_Undefined
  };

  const char* GetLabel(eId Id);

  template <typename ... tags> inline const str::string_& GetTranslation(
    eId Id,
    str::dString& Translation,
    const tags &... Tags)
  {
    return sclm::GetBaseTranslation(GetLabel(Id), Translation, Tags...);
  }
}

#endif
