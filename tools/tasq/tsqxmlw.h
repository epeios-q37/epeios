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

// TaSQ XML Writing

#ifndef TSQXMLW_INC_
# define TSQXMLW_INC_

# include "tsqbndl.h"
# include "tsqtsk.h"

# include "xml.h"

namespace tsqxmlw {
  qENUM( Filter ) {
    fDescription_,
    fId_,
    fReadable_,
    f_amount_,
    f_Undefined_,
  };

# define FF_( name )	ff##name = ( 1 << f##name##_ )

  qENUM( FilterFlag ) {
    FF_( Description ),
    FF_( Id ),
    FF_( Readable ),
    ffAll = ( ( 1 << f_amount_ ) - 1 ),
    ffExport = ffAll & ~( ffId | ffReadable ),
    ffDisplay = ffAll & ~ffDescription
  };

# undef TF_

  void WriteCorpus(xml::rWriter &Writer);

  void WriteCorpus(str::dString &XML);

  void Write(
    tsqtsk::sRow Row,
    const tsqbndl::dBundle &Bundle,
    int Flags,
    xml::rWriter &Writer);

  void Write(
    tsqtsk::sRow Row,
    const tsqbndl::dBundle &Bundle,
    int Flags,
    str::dString &XML);

  void Write(
    const tsqbndl::dBundle &Bundle,
    int Flags,
    xml::rWriter &Writer);

  void Write(
    const tsqbndl::dBundle &Bundle,
    int Flags,
    str::dString &XML);
}

#endif
