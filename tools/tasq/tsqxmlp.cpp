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

qENUM( Realm ) {
  rTagClosed,
  rValue,
  rClosingTag,
  rProcessed,
  r_amount,
  r_Undefined
};

typedef bso::sU8 sAmount_;
qCDEF(sAmount_, AmountMax_, bso::U8Max);

template <typename item, int amount, item undefined> struct sElement_
{
private:
  item Tag_;
  xml::sVRow_ Attributes_[amount];
  sAmount_ Amount_;
public:
  void reset(bso::sBool P = true)
  {
    Tag_ = undefined;
    memset(Attributes_, -1, sizeof(Attributes_));
    Amount_ = 0;
  }
  void Init(void)
  {
    Tag_ = undefined;
    memset(Attributes_, -1, sizeof(Attributes_));
    Amount_ = 0;
  }
  sAmount_ GetAmount(void) const
  {
    return Amount_;
  }
  bso::sBool HasTag(void) const
  {
    return Tag_ != undefined;
  }
  void SetTag(item Item)
  {
    if ( Item > amount )
      qRFwk();

    if ( HasTag() )
      qRFwk();

    Tag_ = Item;
  }
  item GetTag(void) const
  {
    if ( !HasTag() )
      qRFwk();

    return Tag_;
  }
  bso::sBool HasAttribute(item Item) const
  {
    if ( Item > amount )
      qRFwk();

    return Attributes_[Item] != qNIL;
  }
  void SetAttribute(
    item Item,
    xml::sVRow_ Row)
  {
    if ( HasAttribute(Item) )
      qRFwk();

    if ( Amount_ >= AmountMax_ )
      qRFwk();

    Attributes_[Item] = Row;
  }
  xml::sVRow_ GetAttribute(item Item) const
  {
    if ( !HasAttribute(Item) )
      qRFwk();

     return Attributes_[Item];
  }
};

qROW( TRow_ );

template <typename item, int amount, item undefined> qTCLONE(stkbch::qBSTACKw(sElement_<qCOVER3(item,amount,undefined)>, sTRow_), rElements_);

template <typename item, int amount, item undefined> class rBundle
{
private:
  xml::rValues_ Values_;
  rElements_<item,amount,undefined> Elements_;
  sElement_<item,amount,undefined> Element_;  // Current element.
  xml::sVRow_ Value_; // Current element value.
public:
  void reset(bso::sBool P = true )
  {
    tol::reset(P, Values_, Elements_, Element_, Value_);
  }
  qCDTOR( rBundle );
  void Init(void)
  {
    tol::Init(Values_, Elements_, Element_, Value_);
  }
  bso::sBool IsEmpty(void) const
  {
    return Elements_.Amount() == 0;
  }
  void SetTag(item Item)
  {
    return Element_.SetTag(Item);
  }
  item Tag(void) const
  {
    return Element_.GetTag();
  }
  void SetValue(const str::dString &Value)
  {
    if ( Value_ != qNIL )
      qRFwk();

    Value_ = Values_.Push(Value);
  }
  const str::dString &Value(void) const
  {
    if ( Value_ == qNIL )
      return str::Empty;
    else
      return Values_(Value_);
  }
  bso::sBool HasAttribute(item Item) const
  {
    return Element_.HasAttribute(Item);
  }
  void SetAttribute(
    item Item,
    const str::dString &Value)
  {
    return Element_.SetAttribute(Item, Values_.Push(Value));
  }
  const str::dString &Attribute(item Item) const
  {
    if ( HasAttribute(Item) )
      return Values_(Element_.GetAttribute(Item));
    else
      return str::Empty;
  }
  template <typename t> bso::sBool Attribute(
    item Item,
    t &Number,
    qRPD) const
  {
    if ( !HasAttribute(Item) ) {
      if ( qRPT )
        qRFwk();
      else
        return false;
    }

    Attribute(Item).ToNumber(Number);

    return true;
  }
  bso::sBool Attribute(
    item Item,
    bso::tEnum &Number,
    qRPD) const
  {
    if ( !HasAttribute(Item) ) {
      if ( qRPT )
        qRFwk();
      else
        return false;
    }

    Attribute(Item).ToNumber(Number);

    return true;
  }
  template <typename type> type Attribute(item Item) const
  {
    type Value;

    Attribute(Item, Value);

    return Value;
  }
  void Pop(void)
  {
    sAmount_ Amount = Element_.GetAmount();

    if ( Value_ != qNIL ) {
      Values_.Pop();
      Value_ = qNIL;
    }

    while ( Amount-- )
      Values_.Pop();

    Elements_.Pop(Element_);
  }
  void Push(void)
  {
    if ( Element_.HasTag() ) {
      Elements_.Push(Element_);
      Element_.Init();

      if ( Value_ != qNIL ) {
        Values_.Pop();
        Value_ = qNIL;
      }
    } else if ( !IsEmpty() )
      qRFwk();
  }
};

template <typename item, int amount, item undefined> class rXParser_
: public rBundle<item,amount,undefined>
{
private:
  qRMV(xml::rParser, P_, Parser_);
  item (*GI_)(const str::dString &Pattern);
  bso::sBool Pop_;
  item GetItem_(const str::dString &Pattern)
  {
    if ( GI_ == NULL )
      qRFwk();

    return GI_(Pattern);
  }
public:
  void reset(bso::sBool P = true)
  {
    tol::reset(P, Parser_, GI_,Pop_);
    rBundle<item,amount,undefined>::reset(P);
  }
  qCDTOR( rXParser_ );
  void Init(
    xml::rParser &Parser,
    item GetItem(const str::dString &Pattern))
  {
    Parser_ = &Parser;
    GI_ = GetItem;
    Pop_ = false;
    rBundle<item,amount,undefined>::Init();
  }
  eRealm Parse(void)
  {
    eRealm Realm = r_Undefined;
    bso::sBool Continue = true;

    if ( Pop_ ) {
      this->Pop();
      Pop_ = false;
    }

    while ( Continue ) {
      switch( P_().Parse(xml::tfAllButUseless) ) {
      case xml::tStartTag:
        this->Push();
        this->SetTag(GetItem_(P_().TagName()));
        break;
      case xml::tAttribute:
        this->SetAttribute(GetItem_(P_().AttributeName()), P_().Value());
        break;
      case xml::tStartTagClosed:
        Realm = rTagClosed;
        Continue = false;
        break;
      case xml::tValue:
      case xml::tCData:
        this->SetValue(P_().Value());
        Realm = rValue;
        Continue = false;
        break;
      case xml::tEndTag:
        if ( this->IsEmpty() ) {
          Realm = rProcessed;
        } else {
          Realm = rClosingTag;
          Pop_ = true;
        }
        Continue = false;
        break;
      case xml::t_Processed:
        if ( !this->IsEmpty() )
          qRFwk();

        Realm = rProcessed;
        Continue = false;
        break;
      default:
        qRFwk();
        break;
      }
    }

    return Realm;
  }
};

typedef rXParser_<eToken,tsqxmlc::t_amount,tsqxmlc::t_Undefined> rXParser;

#if 0
class sCallback
: public xml::cXParser<eToken,tsqxmlc::t_amount,tsqxmlc::t_Undefined>
{
private:
  qRMV(dBundle, B_, Bundle_);
  sLinks_ Links_;
  sTRow Row_;
protected:
  virtual void XMLOnStartTagClosed(
    eToken Tag,
    xml::sTRow Row,
    const rPBundle &PBundle) override
  {
    switch( Tag ) {
    case tTasks:
    case tItems:
      break;
    case tItem:
      Row_ = HandleItem_(PBundle, Row, B_(), Row_, Links_);
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
    xml::sTRow Row,
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
    tol::reset(P, Bundle_, Links_, Row_);
  }
  void Init(dBundle &Bundle)
  {
    Bundle_ = &Bundle;
    tol::Init(Row_);

    Links_.Init(tsqstts::GetType, tsqstts::GetUnit);
  }
};
#endif

namespace {
  void HandleStatus_(
    rXParser &Parser,
    dBundle &Bundle,
    sTRow Row,
    const sLinks_ &Links)
  {
  qRH;
    sStatus Status;
    sSpan Span;
    eUnit Unit = u_Undefined;
  qRB;
    Status.Init();

    if ( Parser.HasAttribute(eToken::tType) )
      switch ( Links.Type.Get(Parser.Attribute<bso::tEnum>(eToken::tType)) ) {
      case tPending:
        Status.Init(tPending);
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
      case tRecurrent:
        Parser.Attribute(tSpan, Span);
        Links.Unit.Get(Parser.Attribute<bso::tEnum>(eToken::tUnit));

        Status.Init(Span, Unit);
        break;
      case tCompleted:
        Status.Init(tCompleted);
        break;
      default:
        qRFwk();
        break;
      }

    Bundle.UpdateTaskStatus(Row, Status);
  qRR;
  qRT;
  qRE;
  }
}


namespace {
  namespace task {
    namespace status {
      namespace items {
        template <typename links> void Parse(
          rXParser &Parser,
          eToken RootTag,
          eToken ItemTag,
          links &Links)
        {
          bso::tEnum Id = 0;

          if ( Parser.Tag() != RootTag )
            qRGnr();

          do {
            switch( Parser.Parse() ) {
            case rTagClosed:
              if ( Parser.Tag() != ItemTag )
                qRGnr();

              Parser.Attribute(tId, Id);

              Links.Set(Id, Parser.Attribute(tLabel));
              break;
            case rClosingTag:
              break;
            default:
              qRGnr();
              break;
            }
          } while ( Parser.Tag() != RootTag );
        }
      }

      void Parse(
        rXParser &Parser,
        sLinks_ &Links)
      {
        if ( Parser.Tag() != tStatus )
          qRGnr();

        do {
          switch( Parser.Parse() ) {
          case rTagClosed:
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
          case rClosingTag:
              break;
          default:
            qRGnr();
            break;
          }
        } while ( Parser.Tag() != tStatus );
      }
    }

    void Parse(
      rXParser &Parser,
      sLinks_ &Links)
    {
      if ( Parser.Tag() != tTask )
        qRGnr();

      do {
        switch( Parser.Parse() ) {
        case rTagClosed:
          switch ( Parser.Tag() ) {
          case tStatus:
            status::Parse(Parser, Links);
            break;
          default:
            qRGnr();
            break;
          }
          break;
        case rClosingTag:
            break;
        default:
          qRGnr();
          break;
        }
      } while ( Parser.Tag() != tStatus );
    }
  }

  void ParseCorpus_(
    rXParser &Parser,
    sLinks_ &Links)
  {
    if ( Parser.Tag() != tCorpus )
      qRGnr();

    do {
      switch( Parser.Parse() ) {
      case rTagClosed:
        switch ( Parser.Tag() ) {
        case tTask:
          task::Parse(Parser, Links);
          break;
        default:
          qRGnr();
          break;
        }
        break;
      case rClosingTag:
          break;
      default:
        qRGnr();
        break;
      }
    } while ( Parser.Tag() != tCorpus );
  }
}

namespace {
  void ParseTasks_(
    rXParser &Parser,
    const sLinks_ &Links,
    dBundle &Bundle)
  {
    tsqtsk::sRow Row = qNIL;

    if ( Parser.Tag() != tTasks )
      qRGnr();

    do {
      switch( Parser.Parse() ) {
      case rTagClosed:
        switch( Parser.Tag() ) {
        case tItems:
          break;
        case tItem:
          Row = Bundle.Add(Parser.Attribute(tTitle), Row);
          break;
        case tStatus:
          HandleStatus_(Parser, Bundle, Row, Links);
          break;
        case tDescription:
          break;
        default:
          qRGnr();
          break;
        }
        break;
      case rValue:
        if ( Parser.Tag() != tDescription )
          qRGnr();

        Bundle.UpdateTaskDescription(Row, Parser.Value());
        break;
      case rClosingTag:
        switch( Parser.Tag() ) {
        case tItems:
          break;
        case tItem:
          Row = Bundle.Tasks.Parent(Row);
          break;
        case tDescription:
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
    } while ( Parser.Tag() != tTasks );
  }
}

void tsqxmlp::Parse(
  xml::rParser &BaseParser,
  dBundle &Bundle)
{
qRH;
  rXParser Parser;
  sLinks_ Links;
  bso::sBool Continue = true;
qRB;
  Parser.Init(BaseParser, GetToken);
  Links.Init(tsqstts::GetType, tsqstts::GetUnit);

  if ( Parser.Parse() != rTagClosed )
    qRGnr();

  if ( Parser.Tag() != tTASq )
    qRGnr();

  while ( Continue ) {
    switch( Parser.Parse() ) {
    case rTagClosed:
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
    case rClosingTag:
      break;
    case rProcessed:
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
