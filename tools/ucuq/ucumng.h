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

// UCUq MaNaGer

#ifndef UCUMNG_INC_
# define UCUMNG_INC_

# include "tol.h"

namespace ucumng {
  qENUM(Request) {
    rClose_1,
    rExecute_1,
    rCreate_1,
    rDelete_1,
    r_amount,
    r_Undefined
  };

  const char *GetLabel(eRequest Request);

  eRequest GetRequest(const str::dString &Pattern);

  qENUM(Answer) {
    aOK,
    aError,
    a_amount,
    a_Undefined
  };
}

#endif
