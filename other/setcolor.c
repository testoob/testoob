// Testoob, Python Testing Out Of (The) Box
// Copyright (C) 2005-2006 The Testoob Team
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <windows.h>

// compile with:
//   cl setcolor.c user32.lib kernel32.lib /link /nodefaultlib /entry:main /opt:nowin98

int main()
{
  HANDLE hStdout = GetStdHandle(STD_OUTPUT_HANDLE);

  const char *szCmdLine = GetCommandLine();
  char cCmd = CharPrev(szCmdLine, szCmdLine + lstrlen(szCmdLine))[0];

  switch (cCmd)
  {
    case 'd':
      SetConsoleTextAttribute(hStdout, FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED);
      break;
    case 'r':
      SetConsoleTextAttribute(hStdout, FOREGROUND_RED | FOREGROUND_INTENSITY);
      break;
    case 'g':
      SetConsoleTextAttribute(hStdout, FOREGROUND_GREEN | FOREGROUND_INTENSITY);
      break;
    case 'y':
      SetConsoleTextAttribute(hStdout, FOREGROUND_GREEN | FOREGROUND_RED | FOREGROUND_INTENSITY);
      break;
    case 'b':
      SetConsoleTextAttribute(hStdout, FOREGROUND_BLUE | FOREGROUND_INTENSITY);
      break;
    default:
      return 1;
  }

  return 0;
}
