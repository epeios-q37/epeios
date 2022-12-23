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

// TaSQ STaTuS

#ifndef TSQSTTS_INC_
# define TSQSTTS_INC_

# include "bch.h"
# include "dte.h"
# include "tme.h"
# include "tol.h"

namespace tsqstts {
  qENUM( Type ) {
    tTimeless,   // Task with no time constriant.
    tEvent,     // Task is an event (date and hour).
    tTimely,    // Due task (due date and begin date, which, by default, is the date when the task was crated.
    t_amount,
    t_Undefined,
    t_Default = tTimeless
  };

  const char *GetLabel(eType Type);

  eType GetType(const str::dString &Pattern);

  typedef bso::sU8 sSpan;

  qENUM( Unit ) {
    uDay,
    uWeek,
    uMonth,
    uYear,
    u_amount,
    u_Undefined
  };

  const char *GetLabel(eUnit Unit);

  eUnit GetUnit(const str::dString &Pattern);

  struct sRecurrence
  {
    sSpan Span; // If 0, no recurrence.
    eUnit Unit;
    void reset(bso::sBool = true)
    {
      Span = 0;
      Unit = u_Undefined;
    }
    qCDTOR( sRecurrence );
    void Init(void)
    {
      Span = 0;
      Unit = u_Undefined;
    }
  };

  struct sStatus
  {
  public:
    eType Type;
    union {
      struct {
        dte::sDate Date;
        tme::sTime Time;
        void Init(void)
        {
          tol::Init(Date, Time);
        }
      } Event;
      struct {
        dte::sDate
          Latest, Earliest;
        void Init(void)
        {
          tol::Init(Latest, Earliest);
        }
      } Timely;
    };
    sRecurrence Recurrence;
    void reset(bso::sBool P = true)
    {
      Type = t_Undefined;
      Recurrence.reset(P);
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
      this->Type = Type;

      Recurrence.Init();

      switch( Type ) {
      case tTimeless:
        break;
      case tEvent:
        Event.Init();
        break;
      case tTimely:
        Timely.Init();
        break;
      default:
        qRGnr();
        break;
      }
    }
    void Init(
      dte::sDate Date,
      tme::sTime Time,
      sRecurrence Recurrence = sRecurrence() )
    {
      Type = tEvent;

      Event.Date = Date;
      Event.Time = Time;
      this->Recurrence = Recurrence;
    }
    void Init(
      dte::sDate Latest,
      dte::sDate Earliest,
      sRecurrence Recurrence = sRecurrence() )
    {
      Type = tTimely;

      Timely.Latest = Latest;
      Timely.Earliest = Earliest;
      this->Recurrence = Recurrence;
    }
  };

  qROW( Row );

  typedef bch::qBUNCHd(sStatus, sRow) dStatutes;
}

# ifdef C
#  define TSQSTTS_BUFFER_ C
# endif

# undef C

# define C( name )\
  case tsqstts::t##name:\
    return memcmp( &S1.name, &S2.name, sizeof(S1.name)) == 0;\
    break

inline bso::sBool operator ==(
  const tsqstts::sRecurrence &R1,
  const tsqstts::sRecurrence &R2)
{
  return ( R1.Span == R2.Span ) && ( R1.Span != 0 ? R1.Unit == R2.Unit : true );
}

inline bso::sBool operator ==(
  const tsqstts::sStatus &S1,
  const tsqstts::sStatus &S2)
{
  if ( S1.Type != S2.Type )
    return false;

  switch ( S1.Type ) {
  case tsqstts::tTimeless:
    return true;
    break;
  case tsqstts::tEvent:
    return
      ( S1.Event.Date == S2.Event.Date )
      && ( S1.Event.Time == S2.Event.Time)
      && ( S1.Recurrence == S2.Recurrence);
      break;
  case tsqstts::tTimely:
    return
      ( S1.Timely.Latest == S2.Timely.Latest )
      && ( S1.Timely.Earliest == S2.Timely.Earliest )
      && ( S1.Recurrence == S2.Recurrence);
      break;
  default:
    qRGnr();
    break;
  }

  return false; // To avoid a warning.
}

# undef C

# ifdef TSQSTTS_BUFFER_
#  define C TSQSTTS_BUFFER_
# endif


inline bso::sBool operator !=(
  const tsqstts::sStatus &S1,
  const tsqstts::sStatus &S2)
{
    return !operator ==(S1, S2);
}



#endif
