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


#ifndef TASKS_INC_
# define TASKS_INC_

# include "lstbch.h"
# include "lstcrt.h"
# include "que.h"
# include "str.h"

namespace tasks {
  qROW( SRow );

  typedef lstcrt::qLMCRATEd( str::dString, sSRow ) dStrings;
  qW( Strings );

  qROW( TRow );

  typedef qQUEUEd( sTRow ) dQueue;
  qW( Queue );

  typedef qQUEUEMs( sTRow ) sQManager;

  class sTask {
  public:
    sSRow
      Title,
      Description;
    sTRow Parent;
    sQManager Children;
    void reset(bso::sBool P = true)
    {
      Title = Description = qNIL;
      Parent = qNIL;
      tol::reset( P, Children );
    }
    qCDTOR(sTask);
    void Init(const dQueue &Queue)
    {
      Title = Description = qNIL;
      Parent = qNIL;
      Children.Init(Queue);
    }
  };


  typedef lstbch::qLBUNCHd( sTask, sTRow ) dTasks;
  qW(Tasks);

  qHOOKS3(lstctn::sHooks, Strings, lstbch::sHooks, Tasks, que::sHook, Queue);

  class dBundle {
  private:
    void Retrieve_(
      sTRow Row,
      sQManager &Manager)
    {
      if ( Row == qNIL )
        Manager = S_.Main;
      else if ( Tasks.Exists(Row) )
        Manager = Tasks(Row).Children;
      else
        qRGnr();
    }
    void Store_(
      const sQManager &Manager,
      sTRow Row)
    {
      if ( Row == qNIL )
        S_.Main = Manager;
      else if ( Tasks.Exists(Row) ) {
        sTask Task;
        Task.Init(Queue);

        Tasks.Recall(Row, Task);
        Task.Children = Manager;
        Tasks.Store(Task, Row);
      } else
        qRGnr();
    }
    sSRow Add_(const str::dString &String)
    {
      sSRow Row = Strings.New();

      Strings(Row) = String;

      return Row;
    }
    const sTask GetTask_(sTRow Row) const
    {
      sTask Task;

      Task.Init(Queue);

      Tasks.Recall(Row, Task);

      return Task;
    }
  public:
    struct s {
      dStrings::s Strings;
      dTasks::s Tasks;
      dQueue::s Queue;
      sQManager Main; // Main tasks
    } &S_;
    dStrings Strings;
    dTasks Tasks;
    dQueue Queue;
    dBundle( s &S)
    : S_(S),
      Strings(S.Strings),
      Tasks(S.Tasks),
      Queue(S.Queue)
    {}
    void reset(bso::sBool P = true)
    {
      tol::reset(P, Strings, Tasks, Queue, S_.Main);
    }
    void plug(sHooks &Hooks)
    {
      Strings.plug(Hooks.Strings_);
      Tasks.plug(Hooks.Tasks_);
      Queue.plug(Hooks.Queue_);
    }
    void plug( qASd *AS )
    {
      Strings.plug(AS);
      Tasks.plug(AS);
      Queue.plug(AS);
    }
    dBundle &operator =(const dBundle &B)
    {
      Strings = B.Strings;
      Tasks = B.Tasks;
      Queue = B.Queue;
      S_.Main = B.S_.Main;

      return *this;
    }
    void Init(void)
    {
      tol::Init(Strings, Tasks, Queue);
      S_.Main.Init(Queue);
    }
    sTRow Add(
      const str::dString &Title,
      const str::dString &Description,
      sTRow Row = qNIL)
    {
      sQManager Manager;
      sTask Task;
      sTRow New = qNIL;

      Manager.Init(Queue);
      Retrieve_(Row, Manager);

      Task.Init(Queue);

      Task.Title = Add_(Title);

      if ( Description.Amount() )
        Task.Description = Add_(Description);

      Task.Parent = Row;

      New = Tasks.Add(Task);
      Queue.Allocate(Tasks.Extent());

      Manager.BecomeLast(New, Queue);

      Store_(Manager, Row);

      return New;
    }
    sTRow Add(
      const str::dString &Title,
      sTRow Row)
    {
      return Add(Title, str::Empty, Row);
    }
    sTRow Parent(sTRow Row) const
    {
      return GetTask_(Row).Parent;
    }
    sTRow Next(sTRow Row = qNIL) const
    {
      if ( Row == qNIL )
        return S_.Main.First(Queue);
      else
        return Queue.Next(Row);
    }
    sTRow Previous(sTRow Row = qNIL) const
    {
      if ( Row == qNIL )
        return S_.Main.Last(Queue);
      else
        return Queue.Previous(Row);
    }
    sTRow First(sTRow Row) const
    {
      if ( Row == qNIL )
        return S_.Main.First(Queue);
      else
        return GetTask_(Row).Children.First(Queue);
    }
    sTRow Last(sTRow Row) const
    {
      if ( Row == qNIL )
        return S_.Main.Last(Queue);
      else
        return GetTask_(Row).Children.Last(Queue);
    }
  };

  qW(Bundle);

  extern wBundle Bundle;
}

#endif
