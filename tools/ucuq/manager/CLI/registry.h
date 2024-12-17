/*
	Copyright (C) 2021 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'ucuqm' tool.

    'ucuqm' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'ucuqm' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'ucuqm'.  If not, see <http://www.gnu.org/licenses/>.
*/


#ifndef REGISTRY_INC_
# define REGISTRY_INC_

# include "sclr.h"

namespace registry {
	using namespace sclr;

	namespace parameter {
		using namespace sclr::parameter;

    extern rEntry JSON;
    extern rEntry HostService;
    extern rEntry Token;
    extern rEntry Id;
    extern rEntry In;
    extern rEntry Out;
    extern rEntry Expression;
    extern rEntry NewProxy;
    extern rEntry VToken;
    extern rEntry NewToken;
  }

	namespace definition {
		using namespace sclr::definition;
    namespace scripts {
      extern rEntry TaggedScript;
      extern rEntry TaggedScriptExpression;
    }
	}

  const str::dString &GetScript(
    const str::dString &Label,
    str::dString &Script);

  const str::dString &GetScriptExpression(
    const str::dString &Label,
    str::dString &Expression);
}

#endif
