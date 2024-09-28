/*
  Copyright (C) 2024 Claude SIMON (http://q37.info/contact/).

  This file is part of the 'UCUq' tool.

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


#include "backend.h"

#include "registry.h"

#include "sclm.h"

using namespace backend;

namespace {
  common::rCallers Backends_;
}

sRow backend::New(sck::rRWDriver *Driver)
{
  return Backends_.New(Driver);
}

sRow backend::Get(void)
{
  return Backends_.Get();
}

fdr::rRWDriver &backend::Get(sRow Row)
{
  return Backends_.Get(*Row);
}

qGCTOR(backend)
{
  Backends_.Init();
}
