/*
	Copyright (C) 1999 Claude SIMON (http://q37.info/contact/).

	This file is part of the Epeios framework.

	The Epeios framework is free software: you can redistribute it and/or
	modify it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, either version 3 of the
	License, or (at your option) any later version.

	The Epeios framework is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
	Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with the Epeios framework.  If not, see <http://www.gnu.org/licenses/>
*/

#define MSCABC_COMPILATION_

#include "mscabc.h"

#include "mthrtn.h"

using namespace mscabc;

namespace _ {
  bso::sS8 Convert(
    const mscmld::sNote &Note,
    mscmld::eAccidental Accidental,
    const char *Separator,
    txf::sWFlow &Flow)
  {
    const char *Label = NULL;
    bso::sS8 RawDuration = 0;
    mthrtn::wRational Duration;
    bso::sS8 RelativeOctave;
    bso::pInteger NBuffer, DBuffer;
    char PitchNotation[] = {0,0,0};
    mscmld::sAltPitch Pitch;

    Pitch.Init();

    mscmld::Convert(Note, Accidental, Pitch);

    Label = mscmld::GetLabel(Pitch);
    RawDuration = Note.Duration.Base;

    Duration.Init(mthrtn::wRational(1,1 << (RawDuration - 1)) * mthrtn::wRational(( 2 << Note.Duration.Modifier ) - 1, 1 << Note.Duration.Modifier));
    RelativeOctave = Pitch.Octave - 4;

    if ( Pitch.Name == mscmld::pnRest ) {
      Flow << "z";
    } else {
      if ( RelativeOctave < 0 )
        return RelativeOctave;

      if ( RelativeOctave > 3 )
        return RelativeOctave - 3;

      if ( strlen(Label) != 1 )
        qRGnr();

      switch ( RelativeOctave ) {
      case 0:
        PitchNotation[1] = ',';
      case 1:
        PitchNotation[0] = toupper(Label[0]);
        break;
      case 3:
        PitchNotation[1] = '\'';
      case 2:
        PitchNotation[0] = tolower(Label[0]);
        break;
      default:
        qRGnr();
        break;
      }

      switch ( Pitch.Accidental ) {
      case mscmld::aSharp:
        Flow << '^';
        break;
      case mscmld::aFlat:
        Flow << '_';
        break;
      case mscmld::aNatural:
        break;
      default:
        qRGnr();
        break;
      }

      Flow << PitchNotation;
    }

    Flow << bso::Convert(Duration.N.GetU32(), NBuffer) << '/' << bso::Convert(Duration.D.GetU32(), DBuffer);

    if ( Note.Duration.TiedToNext )
      Flow << '-';

    Flow << " [|]" << Separator;

    return 0;
  }

  namespace _ {
    qCDEFC(EscapedNL, "\\n");
    qCDEFC(NL, "\n");
  }

  bso::sS8 Convert(
    const mscmld::dMelody &Melody,
    mscmld::eAccidental Accidental,
    bso::sBool EscapeNL,
    bso::sU8 Width,
    txf::sWFlow &Flow)
  {
    if ( Width == 0 ) // Floating point error on '%' -modulo).
      qRFwk();

    bso::sS8 Return = 0;
    mscmld::sRow Row = Melody.First();
    bso::sUHuge Counter = 1;

    const char *&NL = EscapeNL ? _::EscapedNL : _::NL;

    Flow << "X: 1" << NL << "T:" << NL << "L: 1" << NL << "K: C" << NL;

    if ( Row == qNIL )
      Flow << "[|]";

    while ( ( Return == 0 ) && ( Row != qNIL ) ) {
      Return = Convert(Melody(Row), Accidental, Counter++ % Width ? " " : NL, Flow);

      Row = Melody.Next(Row);
    }

    return Return;
  }
}

bso::sS8  mscabc::Convert(
  const mscmld::dMelody &Melody,
  mscmld::eAccidental Accidental,
  bso::sU8 Width,
  bso::sBool EscapeNL,
  txf::sWFlow &Flow)
{
  return _::Convert(Melody, Accidental, EscapeNL, Width, Flow);
}
