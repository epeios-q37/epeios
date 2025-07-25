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


#ifndef MODULES_INC_
# define MODULES_INC_

# include "rgstry.h"

namespace modules {
  void Load(const fnm::rName & Name);

  bso::sBool GetModuleContent(
    const str::dString &Name,
    str::dString &Content);

  bso::sBool GetModuleDependencies(
    const str::dString &Name,
    str::dStrings &Dependencies);  // Add dependencies which are not already present.
}

#endif
