/*
  Copyright (C) 2024 Claude SIMON (http://q37.info/contact/).

  This file is part of the 'UCUq' toolkit.

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

#ifndef UCUCMN_INC_
# define UCUCMN_INC_

# include "tol.h"

namespace ucucmn {
  qENUM(Caller) {
    cAdmin,
    cManager,
    cFrontend,
    cBackend,
    c_amount,
    c_Undefined
  };

  const char *GetLabel(eCaller Caller);

  eCaller GetCaller(const str::dString &Pattern);
}

#endif
