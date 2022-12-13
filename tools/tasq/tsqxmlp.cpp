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


#include "tsqxmlp.h"

#include "tsqxmlc.h"

#include "flx.h"
#include "stkbch.h"

using namespace tsqxmlp;

using namespace tsqxmlc;

namespace task = tsqtsk;

namespace {
  namespace _ {
    void ParseItems(
      xml::rParser &Parser,
      tsqbndl::dBundle &Bundle)
    {
    qRH;
      bso::sBool Continue = true;
      stkbch::qBSTACKwl( eToken ) Tokens;
      str::wString Title;
      task::sRow Row = qNIL;
    qRB;
      if ( GetToken(Parser.TagName()) != tItems )
        qRGnr();

      Tokens.Init();

      Tokens.Push(tItems);

      while ( Continue ) {
        switch ( Parser.Parse(xml::tfObvious | xml::tfStartTagClosed) ) {
        case xml::tStartTag:
          Tokens.Push(GetToken(Parser.TagName()));

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
          switch( GetToken(Parser.AttributeName()) ) {
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
          if ( Tokens.Top() != GetToken(Parser.TagName()) )
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
    if ( GetToken(Parser.TagName()) != tTasks )
      qRGnr();

    while ( Continue ) {
      switch ( Parser.Parse(xml::tfObvious) ) {
      case xml::tStartTag:
        switch ( GetToken(Parser.TagName() ) ) {
        case tItems:
          _::ParseItems(Parser, Bundle);
          break;
        default:
          qRGnr();
          break;
      }
      break;
      case xml::tEndTag:
        if ( GetToken(Parser.TagName()) != tTasks )
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

void tsqxmlp::Parse(
  xml::rParser &Parser,
  tsqbndl::dBundle &Bundle)
{
qRH;
  bso::sBool Continue = true;
qRB;
  while ( Continue ) {
    switch ( Parser.Parse(xml::tfObvious) ) {
    case xml::tStartTag:
      switch ( GetToken(Parser.TagName() ) ) {
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
