/*
	Copyright (C) 2022 Claude SIMON (http://q37.info/contact/).

	This file is part of the 'TASq' tool.

    'TASq' is free software: you can redistribute it and/or modify it
    under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    'TASq' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with 'TASq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "tsqxmlc.h"

#include "stsfsm.h"

using namespace tsqxmlc;

#define C_( name ) case t##name: Label= #name; break

const char *tsqxmlc::GetLabel(eToken Token)
{
  const char *Label = NULL;

  switch ( Token ) {
  C_( TasQ );
  C_( Corpus );
  C_( Status );
  C_( Types );
  C_( Type );
  C_( Tasks );
  C_( Task );
  C_( Items );
  C_( Item );
  C_( RootTask );
  case tId:
    Label = "id";
    break;
  C_( Label );
  C_( Selected );
  C_( Title );
  C_( Description );
  C_( Date );
  C_( Time );
  C_( Latest );
  C_( Earliest );
  C_( Span );
  C_( Unites );
  C_( Unit );
    break;
/*
  C_( );
*/
  default:
    qRGnr();
  }

  return Label;
}

#undef C_

namespace {
  namespace _ {
    stsfsm::wAutomat Automat;
  }

  void FillAutomat_( void )
  {
    _::Automat.Init();
    stsfsm::Fill<eToken>(_::Automat, t_amount, GetLabel);
  }
}

eToken tsqxmlc::GetToken(const str::dString &Pattern)
{
  return stsfsm::GetId(Pattern, _::Automat, t_Undefined, t_amount);
}

qGCTOR( tasqxmlc )
{
  FillAutomat_();
}
