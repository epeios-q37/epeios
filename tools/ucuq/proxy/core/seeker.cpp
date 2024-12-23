/*
  Copyright (C) 2024 Claude SIMON (http://q37.info/contact/).

  This file is part of the 'UCUq' toolkit.

  'UCUq' is free software: you can redistribute it and/or modify it
  under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  'UCUq' is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with 'UCUq'.  If not, see <http://www.gnu.org/licenses/>.
*/


#include "seeker.h"

#include "cio.h"

using namespace seeker;

namespace {
  mtx::rMutex Mutex_ = mtx::Undefined;

  qROW(SRow_); // String row
  typedef common::sRow sCRow_; // Caller row.

  /*
  R: real token; V: virtual token; Id: id of a device.

  | Is != or == to qNil | Meaning             |
  | ROrV | IdOrR | VorR | ROrV | IDOrR | VorR |
  |------|-------|------|------|-------|------|
  | ==   | !=    | !=   | /    | R     | V    | Link R to V
  | !=   | ==    | !=   | V    | /     | R    | Link V to R
  | !=   | !=    | ==   | R    | Id    | /    | Device
  | !=   | !=    | !=   | V    | Id    | R    | Link V to a device
  */
  struct sTie_
  {
  public:
    sSRow_
      ROrV,
      IdOrR,
      VOrR;
    sCRow_ Caller;
    void reset(bso::sBool = true)
    {
      ROrV = IdOrR = VOrR = qNIL;
      Caller = qNIL;
    }
    qCTOR(sTie_);
    void Init(void)
    {
      ROrV = IdOrR = VOrR = qNIL;
      Caller = qNIL;
    }
#define T_(R) int(R != qNIL)
#define F_(R,P) ( ( T_(R) & 1 ) << P)
#define M_ (F_(ROrV,2) | F_(IdOrR, 1) | T_(VOrR))
    bso::sBool IsRToV(void) const
    {
      return M_ == 3;
    }
    bso::sBool IsVToR(void) const
    {
      return M_ == 5;
    }
    bso::sBool IsD(void) const
    {
      return M_ == 6;
    }
    bso::sBool IsVToD(void) const
    {
      return M_ == 7;
    }
    bso::sBool IsV(void) const
    {
      return IsVToR() || IsVToD();
    }
#undef M_
#undef F_
#undef T_
  };

  lstbch::qLBUNCHw(sTie_, sRow) Ties_;

  str::wLStrings<sSRow_> Strings_;

  typedef crt::qCMITEMs(str::dString, sSRow_) gStrItm_;

  namespace {
    namespace {
      const str::dString &Get_(
        sSRow_ Row,
        gStrItm_ &Item)
      {
        if ( Row == qNIL )
          return str::Empty;
        else {
          Item.Init(Strings_);
          return Item(Row);
        }
      }
    }
  
    const str::dString &GetROrV_(
      sRow Row,
      gStrItm_ &Item)
    {
      return Get_(Ties_(Row).ROrV, Item);
    }

    const str::dString &GetIdOrR_(
      sRow Row,
      gStrItm_ &Item)
    {
      return Get_(Ties_(Row).IdOrR, Item);
    }

    const str::dString &GetVOrR_(
      sRow Row,
      gStrItm_ &Item)
    {
      return Get_(Ties_(Row).VOrR, Item);
    }
  }

  namespace index_ {
    namespace {
      idxbtq::qINDEXw(sRow) Core_;
      sRow Root_;
      bso::sSign SortCompare_(
        const str::dString &ROrV,
        const str::dString &IdOrR,
        const str::dString &VOrR,
        sRow Row)
      {
        gStrItm_ Item;
        bso::sSign Sign = str::Compare(ROrV, GetROrV_(Row, Item));

        if ( Sign == 0 )
          Sign = str::Compare(IdOrR, GetIdOrR_(Row, Item));

        if ( Sign == 0 )
          if ( VOrR.Amount() )
            Sign = str::Compare(VOrR, GetVOrR_(Row, Item));
          else
            qRGnr();

        return Sign;
      }

      bso::sSign SeekCompare_(
        const str::dString &ROrV,
        const str::dString &IdOrR,
        const str::dString &VOrR,
        sRow Row)
      {
        gStrItm_ Item;
        bso::sSign Sign = str::Compare(ROrV, GetROrV_(Row, Item));

        if ( ( Sign == 0 ) && IdOrR.Amount() )
          Sign = str::Compare(IdOrR, GetIdOrR_(Row, Item));

        if ( ( Sign == 0 ) && VOrR.Amount() )
          Sign = str::Compare(VOrR, GetVOrR_(Row, Item));

        return Sign;
      }
    }

    void Init(void)
    {
      Core_.Init();
      Root_ = qNIL;
    }

    void Update(
      const str::dString &ROrV,
      const str::dString &IdOrR,
      const str::dString &VOrR,
      sRow Row)
    {
      Core_.Allocate(Ties_.Extent());

      if ( Root_ == qNIL )
        Root_ = Row;
      else {
        bso::sBool Cont = true;
        idxbtq::qISEEKERs(sRow) Seeker;

        Seeker.Init(Core_, Root_);

        while ( Cont ) {
          switch ( SortCompare_(ROrV, IdOrR, VOrR, Seeker.GetCurrent()) ) {
          case -1:
          case 0:
            if ( Seeker.SearchLesser() == qNIL ) {
              Root_ = Core_.BecomeLesser(Row, Seeker.GetCurrent(), Root_);
              Cont = false;
            }
            break;
          case 1:
            if ( Seeker.SearchGreater() == qNIL ) {
              Root_ = Core_.BecomeGreater(Row, Seeker.GetCurrent(), Root_);
              Cont = false;
            }
            break;
          default:
            qRGnr();
            break;
          }
        }

       Root_ = Core_.Balance(Root_);
      }
    }

    sRow Search(
      const str::dString &ROrV,
      const str::dString &IdOrR,
      const str::dString &VOrR)
    {
      sRow Row = Root_;
      bso::sBool Cont = Row != qNIL;
      idxbtq::qISEEKERs(sRow) Seeker;

      Seeker.Init(Core_, Root_);

      while ( Cont ) {
        switch ( SeekCompare_(ROrV, IdOrR, VOrR, Row) ) {
        case -1:
          Row = Seeker.SearchLesser();
          break;
        case 0:
          Cont = false;
          break;
        case 1:
          Row = Seeker.SearchGreater();
          break;
        default:
          qRGnr();
          break;
        }

        Cont = Cont && ( Row != qNIL );
      }

      return Row;
    }

    void Remove(sRow Row)
    {
      Root_ = Core_.Delete(Row, Root_);

      if ( Root_ != qNIL )
        Root_ = Core_.Balance(Root_);
    }

    sRow GetLesser(sRow Row)
    {
      return Core_.Previous(Row);
    }

    sRow GetGreater(sRow Row)
    {
      return Core_.Next(Row);
    }
  }

  void Init_(void)
  {
    tol::Init(Strings_, Ties_);
    index_::Init();
  }

  void Display_(const sTie_ &Tie)
  {
    cio::COut << "ROrV: ";

    if ( Tie.ROrV != qNIL )
      cio::COut << Strings_(Tie.ROrV);

    cio::COut << "\tIdOrR: ";

    if ( Tie.IdOrR != qNIL )
      cio::COut << Strings_(Tie.IdOrR);

    cio::COut << "\tVOrR: ";

    if ( Tie.VOrR != qNIL )
      cio::COut << Strings_(Tie.VOrR);

    cio::COut << "\tCall.: ";

    if ( Tie.Caller != qNIL )
      cio::COut << *Tie.Caller;
  }
}

void seeker::DisplayTies(void)
{
qRH;
  mtx::rHandle Locker;
  sRow Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = Ties_.First();

  while ( Row != qNIL ) {
    cio::COut << *Row << ":\t";

    Display_(Ties_(Row));

    cio::COut << txf::nl << txf::commit;

    Row = Ties_.Next(Row);
  }
qRR;
qRT;
qRE;
}

namespace {
  const dSet &Get_(
    sRow Row,
    dSet &Set)
  {
    gStrItm_ Item;
    sTie_ Tie = Ties_(Row);

    Set.ROrV = Get_(Tie.ROrV, Item);
    Set.IdOrR = Get_(Tie.IdOrR, Item);
    Set.VOrR = Get_(Tie.VOrR, Item);

    return Set;
  }
}

const dSet &seeker::Get(
  sRow Row,
  dSet &Set)
{
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Get_(Row, Set);
qRR;
qRT;
qRE;
  return Set;
}

sCRow_ seeker::GetCaller(sRow Row)
{
  sTie_ Tie;
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Tie.Init();

  Tie = Ties_(Row);

  if ( Tie.Caller == qNIL )
    qRGnr();
qRR;
qRT;
qRE;
  return Tie.Caller;
}

sRow seeker::GetVToken(
  const str::dString &RToken,
  const str::dString &VToken)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
  gStrItm_ Item;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = index_::Search(VToken, str::Empty, str::Empty);

  if ( Row != qNIL )
    if ( !Ties_(Row).IsV() || ( RToken.Amount() && ( GetVOrR_(Row, Item) != RToken ) ) )
      Row = qNIL;
qRR;
qRT;
qRE;
  return Row;
}

namespace {
  sRow GetRToken_(
    const str::dString &RToken,
    const str::dString &Id)
  {
    sRow Row = index_::Search(RToken, Id, str::Empty);

    if ( Row != qNIL )
      if ( !Ties_(Row).IsD() )
        Row = qNIL;

    return Row;
  }
}

sRow seeker::GetRToken(
  const str::dString &RToken,
  const str::dString &Id)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = GetRToken_(RToken, Id);
qRR;
qRT;
qRE;
  return Row;
}

namespace {
  sRow GetVTokenRToken_(
    sRow VTokenRow,
    const str::dString &IdCandidate)
  {
    gStrItm_ RTokenItem, IdItem;

    const str::dString &Id = GetIdOrR_(VTokenRow, IdItem);

    return GetRToken_(GetVOrR_(VTokenRow, RTokenItem), Id.Amount() ? Id : IdCandidate);
  }
}

sRow seeker::GuessRToken(
  const str::dString &Token,
  const str::dString &Id)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = index_::Search(Token, Id, str::Empty);

  if ( Row == qNIL ) {
    Row = index_::Search(Token, str::Empty, str::Empty);

    if ( Row != qNIL )
      if ( Ties_(Row).IsV() )
        Row = GetVTokenRToken_(Row, Id);
      else
        Row = qNIL;
  } else if ( !Ties_(Row).IsD() )
    Row = GetVTokenRToken_(Row, Id);

  if ( Row != qNIL )
    if ( !Ties_(Row).IsD() )
      qRGnr();
qRR;
qRT;
qRE;
  return Row;
}

const dRows &seeker::GetRTokens(
  const str::dString &RToken,
  dRows &Rows)
{
qRH;
  mtx::rHandle Locker;
  sRow
    PrevRow = qNIL,
    Row = qNIL;
  gStrItm_ Item;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = index_::Search(RToken, str::Empty, str::Empty);

  while ( ( Row != qNIL ) && ( GetROrV_(Row, Item) == RToken ) ) {
    PrevRow = Row;
    Row = index_::GetLesser(Row);
  }

  Row = PrevRow;

  while ( ( Row != qNIL ) && ( GetROrV_(Row, Item) == RToken ) ) {
    if ( Ties_(Row).IsD() )
      Rows.Append(Row);

    Row = index_::GetGreater(Row);
  }
qRR;
qRT;
qRE;
  return Rows;
}

const dRows &seeker::GetVTokens(
  const str::dString &RToken,
  dRows &Rows)
{
qRH;
  mtx::rHandle Locker;
  sRow
    PrevRow = qNIL,
    Row = qNIL;
  gStrItm_ Item;
 qRB;
  Locker.InitAndLock(Mutex_);

  Row = index_::Search(str::Empty, RToken, str::Empty);

  while ( ( Row != qNIL ) && ( GetIdOrR_(Row, Item) == RToken ) ) {
    PrevRow = Row;
    Row = index_::GetLesser(Row);
  }

  Row = PrevRow;

  while ( ( Row != qNIL ) && ( GetIdOrR_(Row, Item) == RToken ) ) {
    if ( Ties_(Row).IsRToV() )
      Rows.Append(index_::Search(Get_(Ties_(Row).VOrR, Item), str::Empty, str::Empty));

    Row = index_::GetGreater(Row);
  }
qRR;
qRT;
qRE;
  return Rows;
}

namespace {
  sRow New_(
    const str::dString &RToken,
    const str::dString &Id,
    sCRow_ Caller)
  {
    sTie_ Tie;

    Tie.Init();

    Tie.ROrV = Strings_.New(RToken);
    Tie.IdOrR = Strings_.New(Id);
    Tie.Caller = Caller;

    return Ties_.Add(Tie);
  }
}

sRow seeker::New(
  const str::dString &RToken,
  const str::dString &Id,
  common::sRow Caller)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = New_(RToken, Id, Caller);

  index_::Update(RToken, Id, str::Empty, Row);
qRR;
qRT;
qRE;
  return Row;
}

namespace {
  sSRow_ Add_(const str::dString &String)
  {
    sSRow_ Row = Strings_.New();

    Strings_(Row) = String;

    return Row;
  }

  void Remove_(sSRow_ Row)
  {
    if ( Row != qNIL )
      Strings_.Remove(Row);
  }
}

sRow seeker::Create(
  const str::dString &VToken,
  const str::dString &RToken,
  const str::dString &Id)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
  sTie_ Tie;
qRB;
  Locker.InitAndLock(Mutex_);

  Tie.Init();

  Tie.ROrV = Add_(VToken);
  Tie.VOrR = Add_(RToken);

  if ( Id.Amount() )
    Tie.IdOrR = Add_(Id);

  Row = Ties_.Add(Tie);

  index_::Update(VToken, str::Empty, str::Empty, Row);

  Tie.Init();

  Tie.IdOrR = Add_(RToken);
  Tie.VOrR = Add_(VToken);

  index_::Update(str::Empty, RToken, VToken, Ties_.Add(Tie));
qRR;
qRT;
qRE;
  return Row;
}

namespace {
  void Delete_(sRow Row)
  {
    sTie_ Tie = Ties_(Row);

    Remove_(Tie.ROrV);
    Remove_(Tie.IdOrR);
    Remove_(Tie.VOrR);

    index_::Remove(Row);

    Ties_.Remove(Row);
  }
}

void seeker::Delete(sRow Row)
{
qRH;
  mtx::rHandle Locker;
  wSet Set;
qRB;
  Locker.InitAndLock(Mutex_);

  if ( Ties_(Row).IsV() ) {
    Set.Init();

    Get_(Row, Set);

    Delete_(index_::Search(str::Empty, Set.VOrR, Set.ROrV));
  }

  Delete_(Row);
qRR;
qRT;
qRE;
}

qGCTOR(seeker)
{
  tol::Init(Ties_, Strings_);
  Mutex_ = mtx::Create();
  index_::Init();
}

qGDTOR(seeker)
{
  if ( Mutex_ != mtx::Undefined )
    mtx::Delete(Mutex_);
}

