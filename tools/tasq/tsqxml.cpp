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


#include "tsqxml.h"

#include "flx.h"

using namespace tsqxml;

namespace task = tsqtsk;

namespace {
  qENUM(Token_) {
    tTasQ,
    tCorpus,
    tStatusTypes,
    tType,
    tTasks,
    tItems,
    tItem,
    tRootId,
    tId,
    tLabel,
    tSelected,
    tTitle,
    tDescription,
    tStatus,
    tTypeId,
    tRaw,
    tReadable,
    t_amount,
    t_Undefined
  };

#define C_( name ) case t##name: Label= #name; break

  const char *GetLabel_(eToken_ Token)
  {
    const char *Label = NULL;

    switch ( Token ) {
    C_( TasQ );
    C_( Corpus );
    C_( StatusTypes );
    C_( Type );
    C_( Tasks );
    C_( Items );
    C_( Item );
    C_( RootId );
    case tId:
      Label = "id";
      break;
    C_( Label );
    C_( Selected );
    C_( Title );
    C_( Description );
    C_( Status );
    C_( TypeId );
    C_( Raw );
    C_( Readable );
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

  namespace _ {
    stsfsm::wAutomat Automat;
  }

  void FillAutomat_( void )
  {
    _::Automat.Init();
    stsfsm::Fill<eToken_>(_::Automat, t_amount, GetLabel_);
  }

  eToken_ GetToken_( const str::dString &Pattern )
  {
    return stsfsm::GetId(Pattern, _::Automat, t_Undefined, t_amount);
  }
}

#define L_(token)  GetLabel_( t##token )
namespace {
  void WriteRoot_(xml::rWriter &Writer )
  {
    Writer.PushTag(L_( TasQ ));
  }
}

void tsqxml::WriteCorpus(xml::rWriter &Writer)
{
  Writer.PushTag(L_( Corpus ));
  Writer.PushTag(L_( StatusTypes));

  for(bso::tEnum I = tsqchrns::t_First; I < tsqchrns::t_amount; I++) {
    Writer.PushTag(L_( Type ) );
    Writer.PutAttribute(L_( Id ), I);
    Writer.PutAttribute(L_( Label ), tsqchrns::GetLabel((tsqchrns::eType)I));
    Writer.PopTag();
  }

  Writer.PopTag();
}

void tsqxml::WriteCorpus(str::dString &XML)
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
        const char *Tag,
        xml::rWriter &Writer)
      {
        dte::pBuffer Buffer;

        Writer.PushTag(Tag);
        Writer.PutAttribute(L_( Raw), Date);
        Writer.PutAttribute(L_( Readable ), Date.ASCII(dte::fDDMMYYYY, Buffer));
        Writer.PopTag();
      }

      void Write(
        tme::sTime Time,
        const char *Tag,
        xml::rWriter &Writer)
      {
        tme::pBuffer Buffer;

        Writer.PushTag(Tag);
        Writer.PutAttribute(L_( Raw ), Time);
        Writer.PutAttribute(L_( Readable ), Time.ASCII(Buffer));
        Writer.PopTag();
      }
    }

    void WriteStatus(
      tsqchrns::sStatus &Status,
      xml::rWriter &Writer)
    {
      Writer.PushTag(L_( Status ));

      Writer.PutAttribute(L_( TypeId ), tsqchrns::GetLabel(Status.Type));

      switch ( Status.Type ) {
      case tsqchrns::tPending:
        qRGnr();
        break;
      case tsqchrns::tCompleted:
        break;
      case tsqchrns::tEvent:
        _::Write(Status.Date, "Data", Writer);
        _::Write(Status.Time, "Time", Writer);
        break;
      }
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
      _::WriteStatus(Status, Writer);
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

void tsqxml::Write(
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

void tsqxml::Write(
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

void tsqxml::Write(
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

void tsqxml::Write(
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

namespace {
  namespace _ {
    void ParseItems(
      xml::rParser &Parser,
      tsqbndl::dBundle &Bundle)
    {
    qRH;
      bso::sBool Continue = true;
      stkbch::qBSTACKwl( eToken_ ) Tokens;
      str::wString Title;
      task::sRow Row = qNIL;
    qRB;
      if ( GetToken_(Parser.TagName()) != tItems )
        qRGnr();

      Tokens.Init();

      Tokens.Push(tItems);

      while ( Continue ) {
        switch ( Parser.Parse(xml::tfObvious | xml::tfStartTagClosed) ) {
        case xml::tStartTag:
          Tokens.Push(GetToken_(Parser.TagName()));

          switch ( Tokens.Top() ) {
          case tItem:
            Title.Init();
            break;
          case tDescription:
          case tItems:
            break;
          default:
            qRGnr();
            break;
          }
          break;
        case xml::tAttribute:
          switch( GetToken_(Parser.AttributeName()) ) {
          case tTitle:
            if ( Tokens.Top() != tItem )
              qRFwk();

            Title.Init(Parser.Value());
            break;
          default:
            qRGnr();
            break;
          }
          break;
        case xml::tStartTagClosed:
          if ( Tokens.Top() == tItem ) {
            if ( Title.Amount() == 0 )
              qRGnr();
            else
              Row = Bundle.Add(Title, Row);
          }
          break;
        case xml::tValue:
        case xml::tCData:
          switch ( Tokens.Top() ) {
          case tDescription:
            Bundle.UpdateTaskDescription(Row, Parser.Value());
            break;
          default:
            break;
          }
          break;
        case xml::tEndTag:
          if ( Tokens.Top() != GetToken_(Parser.TagName()) )
            qRGnr();

          switch ( Tokens.Pop() ) {
          case tItems:
            if ( !Tokens.Amount() )
              Continue = false;
            break;
          case tItem:
            Row = Bundle.Tasks.Parent(Row);
            break;
          case tDescription:
            break;
          default:
            qRGnr();
            break;
          }
          break;
        default:
          qRGnr();
          break;
        }
      }
    qRR;
    qRT;
    qRE;
    }
  }

  void ParseTasks_(
    xml::rParser &Parser,
    tsqbndl::dBundle &Bundle)
  {
  qRH;
    bso::sBool Continue = true;
  qRB;
    if ( GetToken_(Parser.TagName()) != tTasks )
      qRGnr();

    while ( Continue ) {
      switch ( Parser.Parse(xml::tfObvious) ) {
      case xml::tStartTag:
        switch ( GetToken_(Parser.TagName() ) ) {
        case tItems:
          _::ParseItems(Parser, Bundle);
          break;
        default:
          qRGnr();
          break;
      }
      break;
      case xml::tEndTag:
        if ( GetToken_(Parser.TagName()) != tTasks )
          qRGnr();
        Continue = false;
        break;
      case xml::t_Error:
        qRGnr();
        break;
      default:
        qRGnr();
        break;
      }
    }
  qRR;
  qRT;
  qRE;
  }

}

void tsqxml::Parse(
  xml::rParser &Parser,
  tsqbndl::dBundle &Bundle)
{
qRH;
  bso::sBool Continue = true;
qRB;
  while ( Continue ) {
    switch ( Parser.Parse(xml::tfObvious) ) {
    case xml::tStartTag:
      switch ( GetToken_(Parser.TagName() ) ) {
      case tTasks:
        ParseTasks_(Parser, Bundle);
        break;
      default:
        qRGnr();
        break;
    }
    break;
    case xml::tEndTag:
      Continue = false;
      break;
    case xml::t_Error:
      qRGnr();
      break;
    default:
      qRGnr();
      break;
    }
  }
qRR;
qRT;
qRE;
}

qGCTOR( tasqxml )
{
  FillAutomat_();
}
