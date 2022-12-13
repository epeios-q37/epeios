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


#include "tsqxmlw.h"

#include "tsqxmlc.h"

#include "flx.h"

using namespace tsqxmlw;

using namespace tsqxmlc;

namespace task = tsqtsk;

#define L_(token)  GetLabel( t##token )

namespace {
  void WriteRoot_(xml::rWriter &Writer )
  {
    Writer.PushTag(L_( TasQ ));
  }
}

void tsqxmlw::WriteCorpus(xml::rWriter &Writer)
{
  Writer.PushTag(L_( Corpus ));
  Writer.PushTag(L_( StatusTypes));

  for(bso::tEnum I = 0; I < tsqchrns::t_amount; I++) {
    Writer.PushTag(L_( Type ) );
    Writer.PutAttribute(L_( Id ), I);
    Writer.PutAttribute(L_( Label ), tsqchrns::GetLabel((tsqchrns::eType)I));
    Writer.PopTag();
  }

  Writer.PopTag();
}

void tsqxmlw::WriteCorpus(str::dString &XML)
{
qRH;
  flx::rStringTWFlow Flow;
  xml::rWriter Writer;
qRB;
  Flow.Init(XML);
  Writer.Init(Flow, xml::oIndent);

  WriteRoot_(Writer);

  WriteCorpus(Writer);

  Writer.PopTag();
qRR;
qRT;
qRE;
}

namespace {
  namespace _ {
    void WriteDescription(
      const str::dString &Description,
      xml::rWriter &Writer)
    {
      if ( Description.Amount() ) {
        Writer.PushTag(L_( Description ));
        Writer.PutCData(Description);
        Writer.PopTag();
      }
    }

    namespace _ {
      void Write(
        dte::sDate Date,
        eToken Token,
        int Flags,
        xml::rWriter &Writer)
      {
        dte::pBuffer Buffer;

        if ( Flags & ffReadable )
          Writer.PutAttribute(GetLabel(Token), Date.ASCII(dte::fDDMMYYYY, Buffer));
        else
          Writer.PutAttribute(GetLabel(Token), Date);
      }

      void Write(
        tme::sTime Time,
        eToken Token,
        int Flags,
        xml::rWriter &Writer)
      {
        tme::pBuffer Buffer;

        if ( Flags & ffReadable )
          Writer.PutAttribute(GetLabel(Token), Time.ASCII(Buffer));
        else
          Writer.PutAttribute(GetLabel(Token), Time);
      }
    }

    void WriteStatus(
      tsqchrns::sStatus &Status,
      int Flags,
      xml::rWriter &Writer)
    {
      Writer.PushTag(L_( Status ));

      Writer.PutAttribute(L_( TypeId ), (bso::tEnum)Status.Type);

      switch ( Status.Type ) {
      case tsqchrns::tPending:
        qRGnr();
        break;
      case tsqchrns::tCompleted:
        break;
      case tsqchrns::tEvent:
        _::Write(Status.Event.Date, tDate, Flags, Writer);
        _::Write(Status.Event.Time, tTime, Flags, Writer);
        break;
      case tsqchrns::tTimely:
        _::Write(Status.Timely.Latest, tLatest, Flags, Writer);
        _::Write(Status.Timely.Earliest, tEarliest, Flags, Writer);
        break;
      case tsqchrns::tRecurrent:
        Writer.PutAttribute(L_( Span ), Status.Recurrent.Span);
        Writer.PutAttribute(L_( UnitId ), (bso::tEnum)Status.Recurrent.Unit);
        break;
      default:
        qRGnr();
        break;
      }

      Writer.PopTag();
    }
  }

  void WriteItemContent_(
    tsqtsk::sRow Row,
    const tsqbndl::dBundle &Bundle,
    int Flags,
    xml::rWriter &Writer)
  {
  qRH;
    task::sTask Task;
    tsqchrns::sStatus Status;
  qRB;
    if ( Flags & ffId )
      Writer.PutAttribute(L_( Id ), *Row);

    Task.Init();
    Bundle.Tasks.Recall(Row, Task);
    Writer.PutAttribute(L_( Title ), Bundle.Strings(Task.Title));
    if ( ( Flags & ffDescription ) && ( Task.Description != qNIL ) )
      _::WriteDescription(Bundle.Strings(Task.Description), Writer);

    if ( Task.Status != qNIL ) {
      Status.Init();
      Bundle.Statutes.Recall(Task.Status, Status);
      _::WriteStatus(Status,Flags, Writer);
    }
  qRR;
  qRT;
  qRE;
  }

  void Write_(
    task::sRow Row,
    const tsqbndl::dBundle &Bundle,
    int Flags,
    xml::rWriter &Writer)
  {
  qRH;
    dtr::qBROWSERs(task::sRow) Browser;
    bso::sBool Skip = false;
  qRB;
    Browser.Init(Row);

    Row = Bundle.Tasks.Browse(Browser);

    while ( Row != qNIL ) {
      switch ( Browser.Kinship() ) {
        case dtr::kChild:
          Writer.PushTag(L_( Items ) );
          break;
        case dtr::kSibling:
          Writer.PopTag();  // 'Item'
          break;
        case dtr::kParent:
          Writer.PopTag();  // 'Item'
          Writer.PopTag();  // 'Items'.
          Skip = true;
          break;
        default:
          qRGnr();
          break;
      }

      if ( !Skip ) {
        Writer.PushTag(L_( Item ));
        WriteItemContent_(Row, Bundle, Flags, Writer );
      } else
        Skip = false;

      Row = Bundle.Tasks.Browse(Browser);
    }
  qRR;
  qRT;
  qRE;
  }

}

void tsqxmlw::Write(
  task::sRow Row,
  const tsqbndl::dBundle &Bundle,
  int Flags,
  xml::rWriter &Writer)
{
  Writer.PushTag(L_( Tasks) );
  Writer.PushTag(L_( Item ) );

  WriteItemContent_(Row, Bundle, Flags, Writer);

  Write_(Row, Bundle, Flags, Writer);

  Writer.PopTag();
  Writer.PopTag();
}

void tsqxmlw::Write(
  task::sRow Row,
  const tsqbndl::dBundle &Bundle,
  int Flags,
  str::dString &XML)
{
qRH;
  flx::rStringTWFlow Flow;
  xml::rWriter Writer;
qRB;
  Flow.Init(XML);
  Writer.Init(Flow, xml::oIndent);

  Write(Row, Bundle, Flags, Writer);
qRR;
qRT;
qRE;
}

void tsqxmlw::Write(
  const tsqbndl::dBundle &Bundle,
  int Flags,
  xml::rWriter &Writer)
{
  task::sRow Row;

  Writer.PushTag(L_( Tasks) );

  Row = Bundle.RootTask();

  if ( Flags & ffId )
    Writer.PutAttribute(L_( RootId ), *Row);

  Write_(Row, Bundle, Flags, Writer);

  Writer.PopTag();
}

void tsqxmlw::Write(
  const tsqbndl::dBundle &Bundle,
  int Flags,
  str::dString &XML)
{
qRH;
  flx::rStringTWFlow Flow;
  xml::rWriter Writer;
qRB;
  Flow.Init(XML);
  Writer.Init(Flow, xml::oIndent);

  WriteRoot_(Writer);

  Write(Bundle, Flags, Writer);

  Writer.PopTag();
qRR;
qRT;
qRE;
}
