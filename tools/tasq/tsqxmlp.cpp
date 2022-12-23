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


#include "tsqxmlp.h"

#include "tsqxmlc.h"

#include "flx.h"
#include "stkbch.h"
#include "stkcrt.h"

using namespace tsqxmlp;

using namespace tsqxmlc;
using namespace tsqbndl;
using namespace tsqstts;

namespace {
  namespace _ {
    template <typename type, int amount, type undefined> class sLooseLinks
    {
    private:
      type Core_[amount];
      type (* GI_)(const str::dString &Pattern);
    public:
      void reset(bso::sBool = true)
      {
        memset(Core_, undefined, sizeof(Core_));
        GI_ = NULL;
      }
      qCDTOR(sLooseLinks);
      void Init(type (* GetItem)(const str::dString &Pattern))
      {
        reset();
        GI_ = GetItem;
      }
      void Set(
        int i,
        type Item)
      {
        if ( i > sizeof(Core_) )
          qRGnr();

        if ( Core_[i] != undefined )
          qRGnr();

        Core_[i] = Item;
      }
      void Set(
        int i,
        const str::dString &Pattern)
      {
        if ( GI_ == NULL )
          qRGnr();

        return Set(i, GI_(Pattern));
      }
      type Get(int i) const
      {
        if ( i > sizeof(Core_) )
          qRGnr();

        if ( Core_[i] == undefined )
          qRGnr();

        return Core_[i];
      }
    };
  }

  typedef _::sLooseLinks<tsqstts::eType, tsqstts::t_amount, tsqstts::t_Undefined> sTypeLinks_;
  typedef _::sLooseLinks<tsqstts::eUnit, tsqstts::u_amount, tsqstts::u_Undefined> sUnitLinks_;

  struct sLinks_{
  public:
    sTypeLinks_ Type;
    sUnitLinks_ Unit;
    void reset(bso::sBool P = true)
    {
      tol::reset(P, Type, Unit);
    }
    qCDTOR( sLinks_ );
    void Init(
      tsqstts::eType (* GetType)(const str::dString &Pattern),
      tsqstts::eUnit (* GetUnit)(const str::dString &Pattern))
    {
      Type.Init(GetType);
      Unit.Init(GetUnit);
    }
  };
};

namespace {
  typedef xml::rXParser<eToken,tsqxmlc::t_amount,tsqxmlc::t_Undefined> rXParser_;
}

namespace {
  namespace task {
    namespace status {
      namespace items {
        template <typename links> void Parse(
          rXParser_ &Parser,
          eToken RootTag,
          eToken ItemTag,
          links &Links)
        {
          bso::tEnum Id = 0;

          if ( Parser.Tag() != RootTag )
            qRGnr();

          do {
            switch( Parser.Parse() ) {
            case xml::rTagClosed:
              if ( Parser.Tag() != ItemTag )
                qRGnr();

              Parser.Attribute(tId, Id);

              Links.Set(Id, Parser.Attribute(tLabel));
              break;
            case xml::rElementClosed:
              break;
            default:
              qRGnr();
              break;
            }
          } while ( Parser.Tag() != RootTag );
        }
      }

      void Parse(
        rXParser_ &Parser,
        sLinks_ &Links)
      {
        if ( Parser.Tag() != tStatus )
          qRGnr();

        do {
          switch( Parser.Parse() ) {
          case xml::rTagClosed:
            switch ( Parser.Tag() ) {
            case tTypes:
              items::Parse(Parser, tTypes, tsqxmlc::tType, Links.Type);
              break;
            case tUnites:
              items::Parse(Parser, tUnites, tsqxmlc::tUnit, Links.Unit);
              break;
            default:
              qRGnr();
              break;
            }
            break;
          case xml::rElementClosed:
              break;
          default:
            qRGnr();
            break;
          }
        } while ( Parser.Tag() != tStatus );
      }
    }

    void Parse(
      rXParser_ &Parser,
      sLinks_ &Links)
    {
      if ( Parser.Tag() != tTask )
        qRGnr();

      do {
        switch( Parser.Parse() ) {
        case xml::rTagClosed:
          switch ( Parser.Tag() ) {
          case tStatus:
            status::Parse(Parser, Links);
            break;
          default:
            qRGnr();
            break;
          }
          break;
        case xml::rElementClosed:
            break;
        default:
          qRGnr();
          break;
        }
      } while ( Parser.Tag() != tStatus );
    }
  }

  void ParseCorpus_(
    rXParser_ &Parser,
    sLinks_ &Links)
  {
    if ( Parser.Tag() != tCorpus )
      qRGnr();

    do {
      switch( Parser.Parse() ) {
      case xml::rTagClosed:
        switch ( Parser.Tag() ) {
        case tTask:
          task::Parse(Parser, Links);
          break;
        default:
          qRGnr();
          break;
        }
        break;
      case xml::rElementClosed:
          break;
      default:
        qRGnr();
        break;
      }
    } while ( Parser.Tag() != tCorpus );
  }
}

namespace {
  namespace status {
    namespace recurrence {
      void Parse(
        rXParser_ &Parser,
        const sUnitLinks_ &Links,
        sRecurrence &Recurrence)
      {
        Parser.Attribute(tSpan, Recurrence.Span);
        Recurrence.Unit = (eUnit)Parser.Attribute<tsqstts::tUnit>(eToken::tUnit);
      }
    }

    void Parse(
      rXParser_ &Parser,
      const sLinks_ &Links,
      sStatus &Status)
    {
      if ( Parser.Tag() != tStatus )
        qRFwk();

      if ( Parser.HasAttribute(eToken::tType) ) {
        switch ( Links.Type.Get(Parser.Attribute<tsqstts::tType>(eToken::tType)) ) {
        case tTimeless:
          Status.Init(tTimeless);
          break;
        case tEvent:
          dte::tDate Date;
          tme::tTime Time;

          Parser.Attribute(tDate, Date);
          Parser.Attribute(tTime, Time);

          Status.Init(dte::sDate(Date), tme::sTime(Time));
          break;
        case tTimely:
          dte::tDate Latest, Earliest;

          Parser.Attribute(tLatest, Latest);
          Parser.Attribute(tEarliest, Earliest);

          Status.Init(dte::sDate(Latest), dte::sDate(Earliest));
          break;
        default:
          qRFwk();
          break;
        }
      }

      do {
        switch ( Parser.Parse() ) {
        case xml::rTagClosed:
          if ( Parser.Tag() == tRecurrence )
            recurrence::Parse(Parser, Links.Unit, Status.Recurrence);
          break;
        case xml::rElementClosed:
          switch( Parser.Tag() ) {
          case tRecurrence:
          case tStatus:
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
      } while ( Parser.Tag() != tStatus );
    }
  }

  void ParseTasks_(
    rXParser_ &Parser,
    const sLinks_ &Links,
    dBundle &Bundle)
  {
    tsqtsk::sRow Row = qNIL;
    sStatus Status;

    if ( Parser.Tag() != tTasks )
      qRGnr();

    do {
      switch( Parser.Parse() ) {
      case xml::rTagClosed:
        switch( Parser.Tag() ) {
        case tItems:
          break;
        case tItem:
          Row = Bundle.Add(Parser.Attribute(tTitle), Row);
          break;
        case tStatus:
          Status.Init();
          status::Parse(Parser, Links, Status);
          Bundle.UpdateTaskStatus(Row, Status);
          break;
        case tDescription:
          break;
        default:
          qRGnr();
          break;
        }
        break;
      case xml::rValue:
        if ( Parser.Tag() != tDescription )
          qRGnr();

        Bundle.UpdateTaskDescription(Row, Parser.Value());
        break;
      case xml::rElementClosed:
        switch( Parser.Tag() ) {
        case tTasks:
        case tItems:
          break;
        case tItem:
          Row = Bundle.Tasks.Parent(Row);
          break;
        case tStatus:
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
    } while ( Parser.Tag() != tTasks );
  }
}

void tsqxmlp::Parse(
  xml::rParser &BaseParser,
  dBundle &Bundle)
{
qRH;
  rXParser_ Parser;
  sLinks_ Links;
  bso::sBool Continue = true;
qRB;
  Parser.Init(BaseParser, GetToken);
  Links.Init(tsqstts::GetType, tsqstts::GetUnit);

  if ( Parser.Parse() != xml::rTagClosed )
    qRGnr();

  if ( Parser.Tag() != tTASq )
    qRGnr();

  while ( Continue ) {
    switch( Parser.Parse() ) {
    case xml::rTagClosed:
      switch( Parser.Tag() ) {
      case tCorpus:
        ParseCorpus_(Parser, Links);
        break;
      case tTasks:
        ParseTasks_(Parser, Links, Bundle);
        break;
      default:
        qRGnr();
        break;
      }
      break;
    case xml::rElementClosed:
      break;
    case xml::rProcessed:
      Continue = false;
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
/*

void tsqxmlp::Parse(
  xml::rParser &Parser,
  dBundle &Bundle)
{
  sCallback Callback;

  Callback.Init(Bundle);

  xml::Parse<eToken,tsqxmlc::t_amount,tsqxmlc::t_Undefined>(Parser, Callback, GetToken);
}

*/
