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
    tEvent,     // Task is an event (date and hour).
    tTimely,    // Due task (due date and begin date, which, by default, is the date when the task was crated.
    tRecurrent,
    tCompleted, // Task is completed
    t_amount,
    t_Undefined,
    t_Default = tPending
  };

  typedef bso::sU8 sSpan;

  qENUM( Unit ) {
    uDay,
    uWeek,
    uMonth,
    uYear,
    u_amount,
    u_Undefined
  };

  const char *GetLabel(eType Type);

  eType GetType(const str::dString &Pattern);

  struct sStatus
  {
  public:
    eType Type;
    dte::sDate Latest;  // For 'tDue' tasks.
    union {
      struct {
        dte::sDate Date;
        tme::sTime Time;
      } Event;
      struct {
        dte::sDate
          Latest, Earliest;
      } Timely;
      struct {
        sSpan Span;
        eUnit Unit;
      } Recurrent;
    };
    void reset(bso::sBool P = true)
    {
      Type = t_Undefined;
    }
    explicit sStatus(eType Type)
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
    }
    void Init(
      dte::sDate Date,
      tme::sTime Time)
    {
      Type = tEvent;

      Event.Date = Date;
      Event.Time = Time;
    }
    void Init(
      dte::sDate Latest,
      dte::sDate Earliest )
    {
      Type = tTimely;

      Timely.Latest = Latest;
      Timely.Earliest = Earliest;
    }
    void Init(
      sSpan Span,
      eUnit Unit)
    {
      Type = tRecurrent;

      Recurrent.Span = Span;
      Recurrent.Unit = Unit;
    }
  };

  qROW( Row );

  typedef bch::qBUNCHd(sStatus, sRow) dStatutes;
}

# ifdef C
#  define TSQCHRNS_BUFFER_ C
# endif

# undef C

# define C( name )\
  case tsqchrns::t##name:\
    return memcmp( &S1.name, &S2.name, sizeof(S1.name)) == 0;\
    break

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
  C( Event );
  C( Timely );
  C( Recurrent );
  default:
    qRGnr();
    break;
  }

  return false; // To avoid a warning.
}

# undef C

# ifdef TSQCHRNS_BUFFER_
#  define C TSQCHRNS_BUFFER_
# endif


inline bso::sBool operator !=(
  const tsqchrns::sStatus &S1,
  const tsqchrns::sStatus &S2)
{
    return !operator ==(S1, S2);
}



#endif
