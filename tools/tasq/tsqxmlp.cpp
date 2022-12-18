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

typedef xml::rBundle<eToken,tsqxmlc::t_amount,tsqxmlc::t_Undefined> rPBundle;

namespace {
  sTRow HandleItem_(
    const rPBundle &PBundle,
    xml::sTRow TRow,
    dBundle &Bundle,
    sTRow Row)
  {
  qRH;
    str::wString Title;
    sStatus Status;
  qRB;
    Title.Init(PBundle.GetAttribute(TRow, tTitle));

    if ( PBundle.HasAttribute(TRow, eToken::tType) )
      switch ( GetType(PBundle.GetAttribute(TRow, eToken::tType)) ) {
      case tPending:
        Status.Init(tPending);
        break;
      case tEvent:
        dte::tDate Date;
        tme::tTime Time;

        PBundle.GetAttribute(TRow, tDate, Date);
        PBundle.GetAttribute(TRow, tTime, Time);

        Status.Init(dte::sDate(Date), tme::sTime(Time));
        break;
      case tTimely:
        dte::tDate Latest, Earliest;

        PBundle.GetAttribute(TRow, tLatest, Latest);
        PBundle.GetAttribute(TRow, tEarliest, Earliest);

        Status.Init(dte::sDate(Latest), dte::sDate(Earliest));
        break;
      case tRecurrent:
        sSpan Span;
        tsqstts::tUnit Unit;

        PBundle.GetAttribute(TRow, tSpan, Span);
        PBundle.GetAttribute(TRow, eToken::tUnit, Unit);

        Status.Init(Span, (eUnit)Unit);
        break;
      case tCompleted:
        Status.Init(tCompleted);
        break;
      default:
        qRFwk();
        break;
      }

    Row = Bundle.Add(Title, Status, Row);
  qRR;
  qRT;
  qRE;
    return Row;
  }
}

class sCallback
: public xml::cXParser<eToken,tsqxmlc::t_amount,tsqxmlc::t_Undefined>
{
private:
  qRMV(dBundle, B_, Bundle_);
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
    Bundle_ = NULL;
    Row_ = qNIL;
  }
  void Init(dBundle &Bundle)
  {
    Bundle_ = &Bundle;
    Row_ = qNIL;
  }
};

void tsqxmlp::Parse(
  xml::rParser &Parser,
  dBundle &Bundle)
{
  sCallback Callback;

  Callback.Init(Bundle);

  xml::Parse<eToken,tsqxmlc::t_amount,tsqxmlc::t_Undefined>(Parser, Callback, GetToken);
}

