#ifndef CORE_LIBS_PRX_LIBSCEVIDEOOUT_INCLUDE_VIDEOUTWINDOW_HPP
#define CORE_LIBS_PRX_LIBSCEVIDEOOUT_INCLUDE_VIDEOUTWINDOW_HPP

#include <SDL.h>

// Returns the SDL_Window* created by libSceVideoOut, or nullptr if not yet created.
// Defined in VideoOutDriver.cpp, exported from libSceVideoOut.
extern "C" SDL_Window* GetVideoOutSDLWindow();

#endif