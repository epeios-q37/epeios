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


#include "device.h"

#include "registry.h"

#include "sclm.h"

#include "lstcrt.h"
#include "str.h"
#include "idxbtq.h"

using namespace device;

namespace {
  mtx::rMutex Mutex_ = mtx::Undefined; // To protect the too below members;


  namespace seeker_ {
    typedef common::sRow sCRow_; // Caller row.

    namespace {
      qROW(SRow_); // String row
    }

    str::wLStrings<sSRow_> Strings;
  
/*
R: real token; V: virtual token; Id: id of a device.

| Is != or == to qNil | Meaning             |
| ROrV | IdOrR | VorR | ROrV | IDOrR | VorR |
|------|-------|------|------|-------|------|
| ==   | !=    | !=   | /    | R     | V    | Link R to V
| !=   | ==    | !=   | V    | /     | R    | Link V to R
| !=   | !=    | ==   | R    | Id    | /    | A device
| !=   | !=    | !=   | V    | Id    | R    | Link V to a device
*/
    struct sTie {
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
      qCTOR(sTie);
      void Init(void)
      {
        ROrV = IdOrR = VOrR = qNIL;
        Caller = qNIL;
      }
#define T(R) int(R != qNIL)
#define F(R,P) (T(R) << P)
#define M (F(ROrV,2) & F(IdOrR, 1) & T(VOrR))
      bso::sBool IsRToV(void) const
      {
        return M & 3;
      }
      bso::sBool IsVToR(void) const
      {
        return M & 5;
      }
      bso::sBool IsD(void) const
      {
        return M & 6;
      }
      bso::sBool IsVToD(void) const
      {
        return M & 7;
      }
      bso::sBool IsV(void) const
      {
        return IsVToR() || IsVToD();
      }
#undef M
#undef F
#undef T
    };

    void Display(const sTie &Tie)
    {
      cio::COut << "ROrV: ";

      if ( Tie.ROrV != qNIL )
        cio::COut << Strings(Tie.ROrV);

      cio::COut << "\tIdOrR: ";

      if ( Tie.IdOrR != qNIL )
        cio::COut << Strings(Tie.IdOrR);

      cio::COut << "\tVOrR: ";

      if ( Tie.VOrR != qNIL )
        cio::COut << Strings(Tie.VOrR);

      cio::COut << "\tCC: ";

      if ( Tie.Caller != qNIL )
        cio::COut << *Tie.Caller;
    }

    lstbch::qLBUNCHw(sTie, sRow) Ties;

    void DisplayTies(void)
    {
      sRow Row = Ties.First();

      while ( Row != qNIL ) {
        cio::COut << *Row << '\t';

        Display(Ties(Row));

        cio::COut << txf::nl << txf::commit;

        Row = Ties.Next(Row);
      }
    }

    namespace {
      idxbtq::qINDEXw(sRow) Index_;
      sRow IndexRoot_;
    }

    void Init(void)
    {
      tol::Init(seeker_::Strings, Ties, Index_);
      IndexRoot_ = qNIL;
    }

    namespace {
      const str::dString &Get_(sSRow_ Row) {
        if ( Row == qNIL )
          return str::Empty;
        else
          return Strings(Row);
      }
    }

    const str::dString &GetROrV(sRow Row)
    {
      if ( Row == qNIL )
        qRGnr();

      return Get_(Ties(Row).ROrV);
    }

    const str::dString &GetIdOrR(sRow Row)
    {
      if ( Row == qNIL )
        qRGnr();

      return Get_(Ties(Row).IdOrR);
    }

    const str::dString &GetVOrR(sRow Row)
    {
      if ( Row == qNIL )
        qRGnr();

      return Get_(Ties(Row).VOrR);
    }

    sCRow_ GetCaller(sRow Row)
    {
      if ( Row == qNIL )
        qRGnr();

      sTie Tie = Ties(Row);

      if ( Tie.Caller == qNIL )
        qRGnr();

      return Tie.Caller;
    }

    namespace {
      bso::sSign SortCompare_(
        const str::dString &ROrV,
        const str::dString &IdOrR,
        const str::dString &VOrR,
        sRow Row)
      {
        bso::sSign Sign = str::Compare(ROrV, GetROrV(Row));

        if ( Sign == 0 )
          Sign = str::Compare(IdOrR, GetIdOrR(Row));

        if ( Sign == 0 )
          Sign = str::Compare(VOrR, GetVOrR(Row));

        return Sign;
      }
    }

    void UpdateIndex(
      const str::dString &ROrV,
      const str::dString &IdOrR,
      const str::dString &VOrR,
      sRow Row)
    {
      Index_.Allocate(Ties.Extent());

      if ( IndexRoot_ == qNIL )
        IndexRoot_ = Row;
      else {
        bso::sBool Cont = true;
        idxbtq::qISEEKERs(sRow) Seeker;

        Seeker.Init(Index_, IndexRoot_);

        while ( Cont ) {
          switch (SortCompare_(ROrV, IdOrR, VOrR, Seeker.GetCurrent()) ) {
          case -1:
          case 0:
            if ( Seeker.SearchLesser() == qNIL ) {
              IndexRoot_ = Index_.BecomeLesser(Row, Seeker.GetCurrent(), IndexRoot_);
              Cont = false;
            }
            break;
          case 1:
            if ( Seeker.SearchGreater() == qNIL ) {
              IndexRoot_ = Index_.BecomeGreater(Row, Seeker.GetCurrent(), IndexRoot_);
              Cont = false;
            }
            break;
          default:
            qRGnr();
            break;
          }
        }

        IndexRoot_ = Index_.Balance(IndexRoot_);
      }
    }

    namespace {
      bso::sSign SeekCompare_(
        const str::dString &ROrV,
        const str::dString &IdOrR,
        const str::dString &VOrR,
        sRow Row)
      {
        bso::sSign Sign = str::Compare(ROrV, GetROrV(Row));

        if ( ( Sign == 0 ) && IdOrR.Amount() )
          Sign = str::Compare(IdOrR, GetIdOrR(Row));

        if ( ( Sign == 0 ) && VOrR.Amount() )
          Sign = str::Compare(VOrR, GetVOrR(Row));

        return Sign;
      }
    }

    sRow SearchInIndex(
      const str::dString &ROrV,
      const str::dString &IdOrR,
      const str::dString &VOrR )
      {
      sRow Row = IndexRoot_;
      bso::sBool Cont = Row != qNIL;
      idxbtq::qISEEKERs(sRow) Seeker;

      Seeker.Init(Index_, IndexRoot_);

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

        Cont &= Cont && ( Row != qNIL);
      }

      return Row;
    }
        
    void RemoveFromIndex(sRow Row)
    {
      IndexRoot_ = Index_.Delete(Row, IndexRoot_);
    }
  }

  common::rCallers Callers_;
}

namespace {
  sRow New_(
    const dSelector &Selector,
    sck::rRWDriver *Driver)
  {
    seeker_::sTie Tie;

    Tie.Init();

    Tie.ROrV = seeker_::Strings.New(Selector.Token);
    Tie.IdOrR = seeker_::Strings.New(Selector.Id);
    Tie.Caller = Callers_.New(Driver);

    return seeker_::Ties.Add(Tie);
  }

  namespace {
    bso::sBool GetRTokenAndId_(
      const str::dString &Token,
      str::dString &RToken,
      str::dString &Id)
    {
      if ( !Token.Amount() )
        qRGnr();

      sRow Row = seeker_::SearchInIndex(Token, str::Empty, str::Empty);

      if ( Row != qNIL ) {
        seeker_::sTie Tie = seeker_::Ties(Row);

        if ( Tie.VOrR != qNIL ) {
          RToken = seeker_::Strings(Tie.VOrR);

          if ( Tie.IdOrR != qNIL )
            Id = seeker_::Strings(Tie.IdOrR);
        } else
          Row = qNIL;
      }

      return Row != qNIL;
    }
  }

  sRow Get_(const dSelector &Selector)
  {
    sRow Row = qNIL;
  qRH;
    str::wString
      RToken,
      Id;
  qRB;
    tol::Init(RToken, Id);

    if ( GetRTokenAndId_(Selector.Token, RToken, Id) ) {
      if ( Selector.Id.Amount() || Id.Amount() )
        Row = seeker_::SearchInIndex(RToken, Id.Amount() ? Id : Selector.Id, str::Empty);
    } else if ( Selector.Id.Amount() )
      Row = seeker_::SearchInIndex(Selector.Token, Selector.Id, str::Empty);
  qRR;
  qRT;
  qRE;
    return Row;
  }

  namespace {
    void Remove_(seeker_::sSRow_ Row)
    {
      if ( Row != qNIL )
        seeker_::Strings.Remove(Row);
    }
  }

  void WithdrawOne_(sRow Row)
  {
    seeker_::sTie Tie = seeker_::Ties(Row);

    Remove_(Tie.ROrV);
    Remove_(Tie.IdOrR);
    Remove_(Tie.VOrR);

    if ( Tie.Caller != qNIL )
      Callers_.Withdraw(Tie.Caller);

    seeker_::RemoveFromIndex(Row);

    seeker_::Ties.Remove(Row);
  }
}

eAnswer device::GetAnswer(
  flw::rRFlow &Flow,
  const common::gTracker *Tracker)
{
  bso::sU8 Answer = a_Undefined;

  common::Get(Flow, Answer, Tracker);

  if ( Answer > a_amount )
    qRGnr();

  return (eAnswer)Answer;
}

sRow device::New(
  const dSelector &Selector,
  sck::rRWDriver *Driver)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = Get_(Selector);

  if ( Row != qNIL )
    WithdrawOne_(Row);

  Row = New_(Selector, Driver);

  seeker_::UpdateIndex(Selector.Token, Selector.Id, str::Empty, Row);

  cio::COut << "New" << txf::nl;

  seeker_::DisplayTies();
qRR;
qRT;
qRE;
  return Row;
}

common::rCaller *device::Hire(
  const dSelector &Selector,
  const void *UserDiscriminator)
{
  common::rCaller *Caller = NULL;
qRH;
  mtx::rHandle Locker;
  sRow Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = Get_(Selector);

  Locker.Unlock();

  if ( Row != qNIL )
    Caller = Callers_.Hire(seeker_::GetCaller(Row), UserDiscriminator);
qRR;
qRT;
qRE;
  return Caller;
}

void device::_Withdraw_NotUsed(sRow Row)
{
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);
  
  WithdrawOne_(Row);

  cio::COut << "Withdraw:" << txf::nl;

  seeker_::DisplayTies();
qRR;
qRT;
qRE;
}

void device::Withdraw(const dSelector &Selector)
{
qRH;
  mtx::rHandle Locker;
  sRow Row = qNIL;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = Get_(Selector);

  if ( Row != qNIL )
    WithdrawOne_(Row);
qRR;
qRT;
qRE;
}

namespace {
  namespace {
    void WithdrawTokenRef_(
      const str::dString &Token,
      sRow Row)
    {
      if ( seeker_::GetVOrR(Row).Amount() ) {
        Row = seeker_::SearchInIndex(str::Empty, seeker_::GetVOrR(Row), Token);

        if ( Row != qNIL )
          WithdrawOne_(Row);
      }
    }
  }

  void WithdrawToken_(const str::dString &Token)  // 'Token' can be real or virtual.
  {
    sRow Row = qNIL, OldRow = qNIL;

    Row = seeker_::SearchInIndex(Token, str::Empty, str::Empty);

    while ( ( Row != qNIL ) && ( seeker_::GetROrV(Row) == Token ) ) {
      OldRow = Row;
      Row = seeker_::Index_.GetLesser(Row);
    }

    Row = OldRow;

    while ( ( Row != qNIL ) && ( seeker_::GetROrV(Row) == Token ) ) {
      OldRow = Row;
      Row = seeker_::Index_.GetGreater(Row);

      WithdrawTokenRef_(Token, Row);

      WithdrawOne_(OldRow);
    }
  }

  void WithdrawVTokens_(const str::dString &RToken)
  {
    sRow Row = qNIL, OldRow = qNIL;

    Row = seeker_::SearchInIndex(str::Empty, RToken, str::Empty);

    while ( ( Row != qNIL ) && ( seeker_::GetIdOrR(Row) == RToken ) ) {
      OldRow = Row;
      Row = seeker_::Index_.GetLesser(Row);
    }

    Row = OldRow;

    while ( ( Row != qNIL ) && ( seeker_::GetIdOrR(Row) == RToken ) ) {
      OldRow = Row;
      Row = seeker_::Index_.GetGreater(Row);

      WithdrawToken_(seeker_::GetVOrR(OldRow));
    }
  }
}

void device::WithdrawToken(const str::dString &Token)
{
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  WithdrawToken_(Token);
qRR;
qRT;
qRE;
}

void device::WithdrawVTokens(const str::dString &Token)
{
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  WithdrawToken_(Token);
qRR;
qRT;
qRE;
}

namespace {
  sRow CreateVTokenOnly_(
    const str::dString &VToken,
    const str::dString &RToken,
    const str::dString &Id)
  {
    sRow Row = qNIL;
    seeker_::sTie Tie;

    Tie.Init();

    Tie.ROrV = seeker_::Strings.New(VToken);
    Tie.VOrR = seeker_::Strings.New(RToken);

    if ( Id.Amount() )
      Tie.IdOrR = seeker_::Strings.New(Id);

    if ( !Tie.IsV() )
      qRGnr();

    Row = seeker_::Ties.Add(Tie);

    seeker_::UpdateIndex(VToken, str::Empty, str::Empty, Row);

    return Row;
  }

  void CreateVTokenRef_(
    const str::dString &VToken,
    const str::dString &RToken)
  {
    seeker_::sTie Tie;

    Tie.Init();

    Tie.IdOrR = seeker_::Strings.New(RToken);
    Tie.VOrR = seeker_::Strings.New(VToken);

    if ( !Tie.IsRToV() )
      qRGnr();
    
    seeker_::UpdateIndex(str::Empty, RToken, VToken, seeker_::Ties.Add(Tie));
  }
}

bso::sBool device::CreateVToken(
  const str::dString &VToken,
  const str::dString &RToken,
  const str::dString &Id)
{
  sRow Row = qNIL; 
qRH;
 ;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = seeker_::SearchInIndex(VToken, str::Empty, str::Empty);

  if ( Row == qNIL ) {
    cio::COut << "Create vtoken" << txf::nl;
    Row = CreateVTokenOnly_(VToken, RToken, Id);
    CreateVTokenRef_(VToken, RToken);
  } else
    Row == qNIL;

  seeker_::DisplayTies();
qRR;
qRT;
qRE;
  return Row != qNIL;
}

namespace {
  void DeleteVTokenRef_(
    seeker_::sSRow_ RTokenRow,
    seeker_::sSRow_ VTokenRow)
  {
    ctn::qCMITEMs(str::dString, seeker_::sSRow_) RToken, VToken;
    seeker_::sTie Tie;

    RToken.Init(seeker_::Strings);
    VToken.Init(seeker_::Strings);

    Tie.Init();

    sRow Row = seeker_::SearchInIndex(str::Empty, RToken(RTokenRow), VToken(VTokenRow));

    if ( Row != qNIL )
      qRGnr();

    Tie = seeker_::Ties(Row);

    if ( !Tie.IsRToV() )
      qRGnr();

    WithdrawOne_(Row);
  }
}

bso::sBool device::DeleteVToken(const str::dString &VToken)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
qRB;
  Locker.InitAndLock(Mutex_);

  Row = seeker_::SearchInIndex(VToken, str::Empty, str::Empty);

  if ( Row != qNIL ) {
    cio::COut << "Delete vtoken" << txf::nl;

    seeker_::sTie Tie = seeker_::Ties(Row);

    if ( Tie.IsV() ) {
      WithdrawOne_(Row);
      DeleteVTokenRef_(Tie.IdOrR, Tie.VOrR);
    }
  }

  seeker_::DisplayTies();
  qRR;
qRT;
qRE;
  return Row != qNIL;
}

bso::sBool device::IsReal(const str::dString &Token)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
  seeker_::sTie Tie = seeker_::Ties(Row);
qRB;
  Locker.InitAndLock(Mutex_);
  Tie.Init();

  Row = seeker_::SearchInIndex(Token, str::Empty, str::Empty);

  if ( Row != qNIL ) {
    Tie = seeker_::Ties(Row);

    if ( !Tie.IsD() )
      Row = qNIL;
  }
qRR;
qRT;
qRE;
  return Row != qNIL;
}

bso::sBool device::IsVirtual(const str::dString &Token)
{
  sRow Row = qNIL;
qRH;
  mtx::rHandle Locker;
  seeker_::sTie Tie = seeker_::Ties(Row);
qRB;
  Locker.InitAndLock(Mutex_);
  Tie.Init();

  Row = seeker_::SearchInIndex(Token, str::Empty, str::Empty);

  if ( Row != qNIL ) {
    Tie = seeker_::Ties(Row);

    if ( !Tie.IsV() )
      Row = qNIL;
  }
qRR;
qRT;
qRE;
  return Row != qNIL;
}

namespace {
  void GetRTokenIds(
    const str::dString &RToken,
    str::dStrings &Ids)
  {
    sRow Row = seeker_::SearchInIndex(Token, str::Empty, str::Empty);

    while ( ( Row != qNIL ) && ( seeker_::GetROrV(Row) == Token ) ) {
      OldRow = Row;
      Row = seeker_::Index_.GetLesser(Row);
    }

    Row = OldRow;

    while ( ( Row != qNIL ) && ( seeker_::GetROrV(Row) == Token ) ) {
      Tie = seeker_::Ties(Row);


      Row = seeker_::Index_.GetGreater(Row);

      WithdrawTokenRef_(Token, Row);

      WithdrawOne_(OldRow);
    }
  }
}

void device::GetRTokenFeatures(
  const str::dString &Token,
  str::dStrings &Ids,
  str::dStrings &VTokens)
{
qRH;
  mtx::rHandle Locker;
  sRow Row = qNIL, OldRow = qNIL;
  seeker_::sTie Tie = seeker_::Ties(Row);
qRB;
  Locker.InitAndLock(Mutex_);

  Row = seeker_::SearchInIndex(Token, str::Empty, str::Empty);

  while ( ( Row != qNIL ) && ( seeker_::GetROrV(Row) == Token ) ) {
    OldRow = Row;
    Row = seeker_::Index_.GetLesser(Row);
  }

  Row = OldRow;

  while ( ( Row != qNIL ) && ( seeker_::GetROrV(Row) == Token ) ) {
    Tie = seeker_::Ties(Row);


    Row = seeker_::Index_.GetGreater(Row);

    WithdrawTokenRef_(Token, Row);

    WithdrawOne_(OldRow);
  }

  Tie.Init();

  Row = seeker_::SearchInIndex(Token, str::Empty, str::Empty);



  if ( Row != qNIL ) {
    Tie = seeker_::Ties(Row);

    if ( !Tie.IsV() )
      Row = qNIL;
  }
qRR;
qRT;
qRE;
  return Row != qNIL;
}

qGCTOR(device)
{
  Mutex_ = mtx::Create();
  Callers_.Init();
  seeker_::Init();
}

qGDTOR(device) {
  if ( Mutex_ != mtx::Undefined )
    mtx::Delete(Mutex_, true);
}
