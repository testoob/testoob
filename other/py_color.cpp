// py_color.cpp : Defines the entry point for the DLL application.
//

#include <windows.h>
#include "python.h"

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
					 )
{
    return TRUE;
}

static PyObject *
py_color_setColor(PyObject *self, PyObject *args)
{
    int color;
	HANDLE hStdout = GetStdHandle(STD_OUTPUT_HANDLE);

    if (!PyArg_ParseTuple(args, "i", &color))
        return NULL;
	switch (color)
	{
	case 1:
		SetConsoleTextAttribute(hStdout, FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED);
		break;
	case 2:
		SetConsoleTextAttribute(hStdout, FOREGROUND_RED | FOREGROUND_INTENSITY);
		break;
	case 3:
		SetConsoleTextAttribute(hStdout, FOREGROUND_GREEN | FOREGROUND_INTENSITY);
		break;
	case 4:
		SetConsoleTextAttribute(hStdout, FOREGROUND_GREEN | FOREGROUND_RED | FOREGROUND_INTENSITY);
		break;
	default:
		return Py_BuildValue("i", 0);
	}

  return Py_BuildValue("i", 1);
}

static PyMethodDef py_colorMethods[] = {
    {"setColor",  py_color_setColor, METH_VARARGS,
     "Set output text color"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initpy_color(void)
{
    (void) Py_InitModule("py_color", py_colorMethods);
}
