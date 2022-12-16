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

typedef xml::rBundle<eToken,t_amount,t_Undefined> rPBundle;

namespace {
  task::sRow HandleItem_(
    const rPBundle &PBundle,
    xml::sTRow TRow,
    tsqbndl::dBundle &Bundle,
    task::sRow Row)
  {
  qRH;
    str::wString Title;
    tsqchrns::sStatus Status;
    tsqchrns::eType Type = tsqchrns::t_Undefined;
  qRB;
    Title.Init(PBundle.GetAttribute(TRow, tTitle));

    if ( PBundle.HasAttribute(TRow, tType) )
      Type = tsqchrns::GetType(PBundle.GetAttribute(TRow, tType));

    Status.Init();

    Row = Bundle.Add(Title, Status, Row);
  qRR;
  qRT;
  qRE;
    return Row;
  }
}

class sCallback
: public xml::cXParser<eToken,t_amount,t_Undefined>
{
private:
  qRMV(tsqbndl::dBundle, B_, Bundle_);
  task::sRow Row_;
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

  xml::Parse<eToken,t_amount,t_Undefined>(Parser, Callback, GetToken);
}

