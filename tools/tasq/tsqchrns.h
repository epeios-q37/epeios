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

// TaSQ CHRoNoS

#ifndef TSQCHRNS_INC_
# define TSQCHRNS_INC_

# include "bch.h"
# include "dte.h"
# include "tme.h"
# include "tol.h"

namespace tsqchrns {
  qENUM( Type ) {
    tPending,   // Task is pending; NOTA: not directly used by this library; is implicit when sRow == qNIL.
    tCompleted, // Task is completed
    tEvent,     // Task is an event (date and hour).
    tDue,       // Due task (due date and begin date, which, by default, is the date when the task was crated.
    t_amount,
    t_Undefined,
    t_Default = tPending
  };

  const char *GetLabel(eType Type);

  eType GetType(const str::dString &Pattern);

  struct sStatus
  {
  public:
    eType Type;
    dte::sDate Before;  // For 'tDue' tasks.
    union {
      dte::sDate
        After,  // For 'tDue' tasks.
        Date;   // For 'tEvent' tasks.
    };
    tme::sTime Time;    // For 'tEvent' tasks;
    void reset(bso::sBool P = true)
    {
      Type = t_Undefined;
      tol::reset(Before, After, Time);
    }
    sStatus(eType Type)
    {
      Init(Type);
    }
    sStatus(
      dte::sDate Date,
      tme::sTime Time)
    {
      Init(Date, Time);
    }
    sStatus(
      dte::sDate Before,
      dte::sDate After)
    {
      Init(Before, After);
    }
    qCDTOR( sStatus );
    void Init(eType Type = t_Default)
    {
      switch( Type ) {
      case tPending:
      case tCompleted:
        this->Type = Type;
        break;
      default:
        qRGnr();
        break;
      }

      tol::Init(Before, After, Time);
    }
    void Init(
      dte::sDate Date,
      tme::sTime Time)
    {
      tol::Init(Before, After, Time);

      Type = tEvent;

      this->Date = Date;
      this->Time = Time;

    }
    void Init(
      dte::sDate Before,
      dte::sDate After )
    {
      tol::Init(Before, After, Time);

      Type = tDue;

      this->Before = Before;
      this-> After = After;
    }
  };

  qROW( Row );

  typedef bch::qBUNCHd(sStatus, sRow) dStatutes;
}

inline bso::sBool operator ==(
  const tsqchrns::sStatus &S1,
  const tsqchrns::sStatus &S2)
{
  if ( S1.Type != S2.Type )
    return false;

  switch ( S1.Type ) {
  case tsqchrns::tPending:
    return true;
    break;
  case tsqchrns::tCompleted:
    return true;
    break;
  case tsqchrns::tDue:
    return ( S1.Before == S2.Before) && ( S1.After == S2.After );
    break;
  case tsqchrns::tEvent:
    return ( S1.Date == S2.Date ) && ( S1.Time == S2.Time );
    break;
  default:
    qRGnr();
    break;
  }

  return false; // To avoid a warning.
}

inline bso::sBool operator !=(
  const tsqchrns::sStatus &S1,
  const tsqchrns::sStatus &S2)
{
    return !operator ==(S1, S2);
}



#endif
