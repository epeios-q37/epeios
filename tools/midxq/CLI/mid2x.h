/*
	Copyright (C) 2019 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'MIDXq' tool.

    'MIDXq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'MIDXq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'MIDXq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#ifndef MID2X_INC_
# define MID2X_INC_

# include "fnm.h"

namespace mid2x {
    void Convert(
        const fnm::rName &Source,
        const fnm::rName &Target );
}

#endif

