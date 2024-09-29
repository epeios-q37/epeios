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

#include "crt.h"

using namespace backend;

namespace {
  crt::qCRATEw(dSelector, sRow) Selectors_;
}

namespace {
  common::rCallers Backends_;
}

namespace {
  sRow New_(
    const dSelector &Selector,
    sck::rRWDriver *Driver)
  {
    sRow Row = Backends_.New(Driver);

    Selectors_.Allocate(Backends_.Extent());

    Selectors_.Store(Selector, Row);

    return Row;
  }

  namespace {
    bso::sBool Matches(
      const dSelector &S1,
      const dSelector &S2)
    {
      return S1.Token == S2.Token && S1.Id == S2.Id;
    }
  }

  sRow Get_(const dSelector &Selector)
  {
    sRow
      Row = Selectors_.First(),
      LastRow = qNIL;

    tol::sTimeStamp TimeStamp = 0;

    while ( Row != qNIL ) {
      if (
        Matches(Selector, Selectors_.Get(Row))
        && (TimeStamp < Backends_.Get(*Row).TimeStamp) )
      {
        LastRow = Row;
        TimeStamp = Backends_.Get(*Row).TimeStamp;
      }

      Row = Selectors_.Next(Row);
    }

    return LastRow;
  }

}


sRow backend::New(
  const dSelector &Selector,
  sck::rRWDriver *Driver)
{
  sRow Row = Get_(Selector);

  if ( Row != qNIL )
    Delete(Row);

  Row = New_(Selector, Driver);

  Selectors_.Allocate(Backends_.Extent());

  Selectors_.Store(Selector, Row);

  return Row;
}


sRow backend::Get(
  const dSelector &Selector,
  bso::sBool *IsAliveFlag)
{
  sRow Row = Get_(Selector);

  if ( Row != qNIL )
    Backends_.RegisterIsActiveFlag(*Row, IsAliveFlag);

  return Row;
}

fdr::rRWDriver &backend::Get(sRow Row)
{
  return *Backends_.Get(*Row).Driver;
}

void backend::Delete(sRow Row)
{
  Backends_.Delete(*Row);
  Selectors_(Row).reset();
}

qGCTOR(backend)
{
  Backends_.Init();
  Selectors_.Init();
}
