/*
	Copyright (C) 2022 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'mscfdraftq' tool.

    'mscfdraftq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'mscfdraftq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'mscfdraftq'.  If not, see <http://www.gnu.org/licenses/>.
*/

// TaSQ XML Common

#ifndef TSQXMLC_INC_
# define TSQXMLC_INC_

# include "xml.h"

namespace tsqxmlc {
  qENUM( Token ) {
    tTasQ,
    tCorpus,
    tStatusTypes,
    tType,
    tTasks,
    tItems,
    tItem,
    tRootTask,
    tId,
    tLabel,
    tSelected,
    tTitle,
    tDescription,
    tStatus,
    tDate,
    tTime,
    tLatest,
    tEarliest,
    tSpan,
    tUnit,
    t_amount,
    t_Undefined
  };

  const char *GetLabel(eToken Token);

  eToken GetToken(const str::dString &Pattern);
}

#endif
