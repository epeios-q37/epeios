/*
	Copyright (C) 2015 Claude SIMON (http://q37.info/contact/).

	This file is part of fwtchrq.

    fwtchrq is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

    fwtchrq is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with fwtchrq.  If not, see <http://www.gnu.org/licenses/>
*/

#ifndef REGISTRY_INC_
# define REGISTRY_INC_

# include "sclrgstry.h"

namespace registry {
	using namespace sclrgstry;

	namespace {
		using rgstry::entry___;
	}

	extern entry___ Path;
	extern entry___ Output;
	extern entry___ ThreadAmountMax;

	extern entry___ ExclusionsListFileName;
	extern entry___ ExclusionsHandling;
	extern entry___ ExclusionsFileSizeMax;
	extern entry___ ExclusionsNameLengthMax;

	extern entry___ GhostsPrefix;
	extern entry___ GhostsSuffix;
}

#endif
