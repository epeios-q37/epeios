/*
  Copyright (C) 2022 Claude SIMON (http://zeusw.org/epeios/contact.html).

  This file is part of 'MSFGq' software.

  'MSFGq' is free software: you can redistribute it and/or modify it
  under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  'MSFGq' is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with 'MSFGq'.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef MAIN_INC_
# define MAIN_INC_

# include "melody.h"

# include "mscmdd.h"

# include "sclx.h"

# include "bso.h"
# include "tol.h"

namespace main {
  typedef bso::sU8 sWidth;

  qCDEF(sWidth, UndefinedWidth, bso::U8Max);
  qCDEF(sWidth, WidthMin, 10);
  qCDEF(sWidth, WidthMax, 25);
  qCDEF(mscmld::sOctave, BaseOctaveMax, 9);

  class sSession
  : public sclx::sProxy
  {
  public:
    mscmld::sOctave BaseOctave;
    sWidth Width;
    mscmld::sRow Row;
    bso::sBool MidiInAvailable;
    void reset(bso::sBool P = true)
    {
      sProxy::reset(P);
      BaseOctave = mscmld::UndefinedOctave;
      Width = UndefinedWidth;
      Row = qNIL;
      MidiInAvailable = false;
    }
    qCDTOR( sSession );
    void Init(
			xdhcuc::cSingle &Callback,
			const scli::sInfo &Info)
    {
      reset();

      sProxy::Init(Callback, Info, sclx::xfh_Default);
    }
  };

  extern class sActionHelper
  : public sclx::cActionHelper<sSession>
  {
  protected:
		bso::bool__ SCLXOnBeforeAction(
			sSession &Session,
			const char *Id,
			const char *Action ) override
    {
      return true;
    }
		void SCLXOnAfterAction(
			sSession &Session,
			const char *Id,
			const char *Action ) override;
		bso::bool__ SCLXOnClose( sSession &Session ) override
		{
		  return true;
		}
  } ActionHelper;

  typedef sclx::rActionsHandler<sSession> rCore;
  extern rCore Core;

  extern mscmdd::rRFlow MidiRFlow;
}

#endif // MAIN_INC_
