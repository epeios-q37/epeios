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

#ifndef LOCALE_INC_
# define LOCALE_INC_

# include "tol.h"

namespace locale {
  qENUM(Message) {
    mClient,
    mServer,
    mUnknownProtocol, // %1: protocol ('Client')
    mUnknownProtocolVersion, // %1: protocol
    m_amount,
    m_Undefined
  };

  const char* GetLabel(eMessage Message);

  template <typename ... tags> inline const str::string_& GetTranslation(
    eMessage Message,
    str::dString& Translation,
    const tags &... Tags)
  {
    return sclm::GetBaseTranslation(GetLabel(Message), Translation, Tags...);
  }
}

#endif
