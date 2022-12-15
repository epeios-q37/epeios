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
#include "stkcrt.h"

using namespace tsqxmlp;

using namespace tsqxmlc;

namespace task = tsqtsk;

qROW( VRow );

typedef stkcrt::qCSTACKw(str::dString, sVRow) rValues;

template <typename token, token undefined, int amount> struct sTag {
public:
  token Token;
  sVRow Attributes[amount];
  sdr::sSize Amount;
  void reset(bso::sBool P = true)
  {
    Token = undefined;
    memset(Attributes, -1, sizeof(Attributes));
    Amount = 0;
  }
  void Init(void)
  {
    reset();
  }
};

qROW( TRow );

template <typename token, token undefined, int amount> qTCLONE(stkbch::qBSTACKw(sTag<qCOVER3(token,undefined,amount)>, sTRow), rTags);

template <typename token, token undefined, int amount> class rBundle {
private:
  rValues Values_;
  rTags<token,undefined, amount> Tags_;
public:
  void reset(bso::sBool P = true )
  {
    tol::reset(P, Values_, Tags_);
  }
  qCDTOR( rBundle );
  void Init(void)
  {
    tol::Init(Values_, Tags_);
  }
  bso::sBool IsEmpty(void) const
  {
    return Tags_.Amount() == 0;
  }
  bso::sBool HasAttribute(
    sTRow Row,
    token Token) const
  {
    sTag<token,undefined, amount> Tag;

    Tag.Init();
    Tags_.Recall(Row, Tag);

    return Tag.Attributes[Token] != qNIL;
  }
  const str::dString &GetAttribute(
    sTRow Row,
    token Token) const
  {
    sTag<token,undefined, amount> Tag;

    Tag.Init();
    Tags_.Recall(Row, Tag);

    if ( Tag.Attributes[Token] != qNIL )
      return Values_(Tag.Attributes[Token]);
    else
      return str::Empty;
  }
  void Pop(void)
  {
    sTag<token,undefined, amount> Tag;

    Tag.Init();
    Tags_.Pop(Tag);

    while ( Tag.Amount-- )
      Values_.Pop();
  }
  sVRow Push(const str::dString &Value)
  {
    return Values_.Push(Value);
  }
  sTRow Push(const sTag<token,undefined, amount> &Tag)
  {
    return Tags_.Push(Tag);
  }
  sTRow Parent(sTRow Row) const
  {
    return Tags_.Previous(Row);
  }
  sTRow Top(void) const
  {
    return Tags_.Last();
  }
};

template <typename token, token undefined, int amount> class cXParser
{
protected:
  virtual void XMLOnStartTagClosed(
    token Tag,
    sTRow Row,
    const rBundle<eToken, t_Undefined, t_amount> &Bundle) = 0;
  virtual void XMLOnEndTag(
    token Tag,
    sTRow Row,
    const str::dString &Value,
    const rBundle<eToken, t_Undefined, t_amount> &Bundle) = 0;
public:
  void OnStartTagClosed(
    token Tag,
    sTRow Row,
    const rBundle<eToken, t_Undefined, t_amount> &Bundle)
  {
    return XMLOnStartTagClosed(Tag, Row, Bundle);
  }
  void OnEndTag(
    token Tag,
    sTRow Row,
    const str::dString &Value,
    const rBundle<eToken, t_Undefined, t_amount> &Bundle)
  {
    return XMLOnEndTag(Tag, Row, Value, Bundle);
  }
};

template <typename token, token undefined, int amount> void Parse(
  xml::rParser &Parser,
  cXParser<token, undefined, amount> &Callback,
  token (*GetToken)(const str::dString &Pattern))
{
  bso::sBool Continue = true;
  rBundle<token, undefined, amount> Bundle;
  sTag<token,undefined, amount> Tag;
  token Token = undefined;

  Bundle.Init();

  while ( Continue ) {
    switch( Parser.Parse(xml::tfAllButUseless) ) {
    case xml::tStartTag:
      Tag.Init();
      Tag.Token = GetToken(Parser.TagName());
      break;
    case xml::tAttribute:
      Token = GetToken(Parser.AttributeName());

      if ( Tag.Attributes[Token] != qNIL )
        qRFwk();

      Tag.Attributes[Token] = Bundle.Push(Parser.Value());
      Tag.Amount++;
      break;
    case xml::tStartTagClosed:
      Callback.OnStartTagClosed(Tag.Token, Bundle.Push(Tag), Bundle);
      break;
    case xml::tValue:
    case xml::tCData:
      break;
    case xml::tEndTag:
      if ( Bundle.IsEmpty() ) {
        Continue = false;
      } else {
        Callback.OnEndTag(Tag.Token, Bundle.Top(), Parser.Value(), Bundle);
        Bundle.Pop();
      }
      break;
    case xml::t_Processed:
      if ( !Bundle.IsEmpty() )
        qRFwk();

      Continue = false;
      break;
    default:
      qRFwk();
      break;
    }
  }
}

typedef rBundle<eToken, t_Undefined, t_amount> rPBundle;

namespace {
  task::sRow HandleItem_(
    const rPBundle &PBundle,
    sTRow TRow,
    tsqbndl::dBundle &Bundle,
    task::sRow Row)
  {
  qRH;
    str::wString Title;
    tsqchrns::sStatus Status;
    tsqchrns::eType Type = tsqchrns::t_Undefined;
  qRB;
    Title.Init(PBundle.GetAttribute(TRow, tTitle));

//    Type = tsqchrns::GetType(PBundle.GetAttribute(TRow, tType));

    Status.Init();

    Row = Bundle.Add(Title, Status, Row);
  qRR;
  qRT;
  qRE;
    return Row;
  }
}

class sCallback
: public cXParser<eToken, t_Undefined, t_amount>
{
private:
  qRMV(tsqbndl::dBundle, B_, Bundle_);
  task::sRow Row_;
protected:
  virtual void XMLOnStartTagClosed(
    eToken Tag,
    sTRow Row,
    const rPBundle &PBundle) override
  {
    switch( Tag ) {
    case tTasks:
    case tItems:
      break;
    case tItem:
      Row_ = HandleItem_(PBundle, Row, B_(), Row_);
      break;
    case tDescription:
      break;
    default:
      qRGnr();
      break;
    }
  }
  virtual void XMLOnEndTag(
    eToken Tag,
    sTRow Row,
    const str::dString &Value,
    const rPBundle &PBundle) override
  {
    switch( Tag ) {
    case tTasks:
    case tItems:
      break;
    case tItem:
      Row_ = B_().Tasks.Parent(Row_);
      break;
    case tDescription:
      B_().UpdateTaskDescription(Row_, Value);
      break;
    default:
      qRGnr();
      break;
    }

  }
public:
  void reset(bso::sBool P = true)
  {
    Bundle_ = NULL;
    Row_ = qNIL;
  }
  void Init(tsqbndl::dBundle &Bundle)
  {
    Bundle_ = &Bundle;
    Row_ = qNIL;
  }
};

void tsqxmlp::Parse(
  xml::rParser &Parser,
  tsqbndl::dBundle &Bundle)
{
  sCallback Callback;

  Callback.Init(Bundle);

  ::Parse<eToken, t_Undefined, t_amount>(Parser, Callback, GetToken);
}

#if 0
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
      sStatus Status;
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
            Status.Init();
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
#endif
