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


#ifndef TSQTSK_INC_
# define TSQTSK_INC_

# include "tsqstrng.h"

# include "bso.h"
# include "dtr.h"
# include "lstbch.h"
# include "lstcrt.h"
# include "str.h"

namespace tsqtsk {
  qROW( Row );

  typedef dtr::qDTREEd( sRow ) dTree;

  class sTask {
  public:
    tsqstrng::sRow
      Title,
      Description;
    void reset(bso::sBool P = true)
    {
      Title = Description = qNIL;
    }
    qCDTOR(sTask);
    void Init(void)
    {
      Title = Description = qNIL;
    }
  };

  typedef lstbch::qLBUNCHd( sTask, sRow ) dTasks;
  qW(Tasks);

  class dXTasks
  : public dTree,
    public dTasks
  {
  protected:
    virtual void LSTAllocate(
      sdr::sSize Size,
      aem::eMode Mode) override
    {
      dTree::Allocate(Size, Mode);
      dTasks::LSTAllocate(Size, Mode);
    }
  public:
    void reset(bso::sBool P = true)
    {
      dTree::reset(P);
      dTasks::reset(P);
    }
    struct s
    : public dTree::s,
      public dTasks::s
    {};
    dXTasks( s &S)
    : dTree(S),
      dTasks(S)
    {}
    dTasks &operator =(const dXTasks &T)
    {
      dTree::operator =(*this);
      dTasks::operator =(*this);

      return *this;
    }
    void plug(qASd *AS)
    {
      dTasks::plug(AS);
      dTree::plug(AS);
    }
    void Init(void)
    {
      dTree::Init();
      dTasks::Init();
    }
    using dTree::First;
    using dTree::Previous;
    using dTree::Next;
    using dTree::Last;
  };

  qW(XTasks);
}

#endif
